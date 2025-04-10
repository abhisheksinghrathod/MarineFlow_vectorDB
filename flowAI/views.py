import os
import re
from collections import Counter
from dotenv import load_dotenv
from django.db import models
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pgvector.django import CosineDistance
from flowAI.models import ClauseEmbedding
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_keywords(question: str):
    return re.findall(r"\b[A-Z][A-Z]+\b", question.upper())

def num_tokens(text: str):
    return len(text.split()) * 1.3  # rough estimate

class AskQuestionView(APIView):
    def post(self, request):
        question = request.data.get("question", "")
        if not question:
            return Response({"error": "Missing question"}, status=400)

        # Step 1: Create embedding for the question
        embedding = openai.embeddings.create(
            input=question,
            model="text-embedding-3-small"
        ).data[0].embedding

        # Step 2: Fetch top 50 matches across all docs
        matches = (
            ClauseEmbedding.objects
            .annotate(similarity=CosineDistance(F("embedding"), embedding))
            .order_by("similarity")[:50]
        )
        top_matches = list(matches)

        # Step 3: Pick best doc_id based on count of top matches
        doc_id_counts = Counter([m.doc_id for m in top_matches[:20]])
        best_doc_id = doc_id_counts.most_common(1)[0][0]

        # Step 4: Refine matches from best doc_id only
        doc_matches = [m for m in top_matches if m.doc_id == best_doc_id]

        # Step 5: Add fallback keyword-based clauses (short ones)
        keywords = extract_keywords(question)
        if keywords:
            q_filters = models.Q()
            for kw in keywords:
                q_filters |= models.Q(content__icontains=kw)
            keyword_clauses = (
                ClauseEmbedding.objects
                .filter(doc_id=best_doc_id)
                .filter(q_filters)
                .exclude(id__in=[m.id for m in doc_matches])
                .extra(where=["char_length(content) < 800"])
                .order_by("id")[:3]
            )
            doc_matches += list(keyword_clauses)

        # Step 6: Limit context to ~3000 tokens
        context_chunks = []
        token_budget = 3000
        current_tokens = 0
        for m in doc_matches:
            tokens = num_tokens(m.content)
            if current_tokens + tokens > token_budget:
                break
            context_chunks.append(m.content)
            current_tokens += tokens

        context = "\n\n".join(context_chunks)

        system_prompt = (
            "You are a marine logistics assistant answering questions from Recap documents. "
            "Only answer from the context provided. Quote exact figures and dates if available. "
            "If you can't find it, say so."
        )
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

        chat_response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        answer = chat_response.choices[0].message.content.strip()

        matched_data = [
            {"clause": m.content, "score": round(getattr(m, "similarity", 0.0), 4)}
            for m in doc_matches
        ]

        return Response({
            "question": question,
            "doc_id": best_doc_id,
            "keywords": keywords,
            "answer": answer,
            "matches": matched_data
        })
