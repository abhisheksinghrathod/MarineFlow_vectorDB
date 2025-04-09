import os
import re
import openai
from dotenv import load_dotenv
from django.db import models
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pgvector.django import CosineDistance
from flowAI.models import ClauseEmbedding
import tiktoken  # Token-aware truncation

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_keywords(question: str):
    """
    Very basic uppercase keyword extractor. Can be replaced with spaCy/RAKE later.
    """
    return re.findall(r"\b[A-Z][A-Z]+\b", question.upper())


def fit_within_token_limit(chunks, max_tokens=3000, model_name="gpt-4"):
    """
    Return as many chunks as can fit within the max token budget.
    """
    enc = tiktoken.encoding_for_model(model_name)
    token_count = 0
    result = []
    for chunk in chunks:
        chunk_tokens = len(enc.encode(chunk))
        if token_count + chunk_tokens > max_tokens:
            break
        result.append(chunk)
        token_count += chunk_tokens
    return result


class AskQuestionView(APIView):
    def post(self, request):
        question = request.data.get("question", "")
        doc_id = request.data.get("doc_id", "")

        if not question:
            return Response({"error": "Missing question"}, status=400)
        if not doc_id:
            return Response({"error": "Missing doc_id"}, status=400)

        # Step 1: Embed the question
        embedding = openai.embeddings.create(
            input=question,
            model="text-embedding-3-small"
        ).data[0].embedding

        # Step 2: Vector search top 10 for that doc
        matches = (
            ClauseEmbedding.objects
            .filter(doc_id=doc_id)
            .annotate(similarity=CosineDistance(F("embedding"), embedding))
            .order_by("similarity")[:10]
        )
        top_matches = list(matches)

        # Step 3: Extract capitalized keywords from the question
        keywords = extract_keywords(question)

        # Step 4: Add fallback clauses based on keyword presence (up to 3 more)
        if keywords:
            q_filters = models.Q()
            for kw in keywords:
                q_filters |= models.Q(content__icontains=kw)

            keyword_clauses = (
                ClauseEmbedding.objects
                .filter(doc_id=doc_id)
                .filter(q_filters)
                .exclude(id__in=[m.id for m in top_matches])
                .extra(where=["char_length(content) < 800"])
                .order_by("id")[:3]
            )
            top_matches += list(keyword_clauses)

        # Step 5: Token-aware context truncation
        raw_chunks = [m.content for m in top_matches]
        context_chunks = fit_within_token_limit(raw_chunks, max_tokens=3000)

        context = "\n\n".join(context_chunks)

        system_prompt = (
            "You are a marine logistics assistant answering questions from Recap documents. "
            "Use only the context provided. If relevant clauses describe rules for timing, laytime, delays, "
            "or procedures, interpret and summarize them clearly. If you can't find the answer, say so."
        )
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

        chat_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = chat_response.choices[0].message.content.strip()

        matched_data = [
            {
                "clause": m.content,
                "score": round(getattr(m, "similarity", 0.0), 4)
            }
            for m in top_matches
        ]

        return Response({
            "question": question,
            "doc_id": doc_id,
            "keywords": keywords,
            "answer": answer,
            "matches": matched_data
        })
