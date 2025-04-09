import os
import re
import tiktoken
import openai
from tqdm import tqdm
from django.core.management.base import BaseCommand
from flowAI.models import ClauseEmbedding
from django.conf import settings

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
EMBEDDING_MODEL = "text-embedding-ada-002"
MAX_TOKENS_PER_CHUNK = 500

# Inline tokenizer using tiktoken
encoding = tiktoken.encoding_for_model(EMBEDDING_MODEL)

def num_tokens(text):
    return len(encoding.encode(text))

def get_embedding(text, model=EMBEDDING_MODEL):
    response = openai.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

def split_clauses(text):
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # First pass: paragraph-based splitting
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    clauses = []
    for para in paragraphs:
        # Priority extraction: lines like "~ LAYCAN: 20/22 MAY 2023"
        lines = para.split("\n")
        for line in lines:
            if re.match(r"^[~*-]?\s*[A-Z\s\-/]+:.*", line.strip()):
                clauses.append(line.strip())

        # Add the full paragraph if it's not already covered
        if num_tokens(para) < MAX_TOKENS_PER_CHUNK:
            clauses.append(para.strip())
        else:
            # Chunk long text
            words = para.split()
            chunk = []
            token_count = 0
            for word in words:
                word_tokens = num_tokens(word + " ")
                if token_count + word_tokens > MAX_TOKENS_PER_CHUNK:
                    if chunk:
                        clauses.append(" ".join(chunk))
                        chunk = []
                        token_count = 0
                chunk.append(word)
                token_count += word_tokens
            if chunk:
                clauses.append(" ".join(chunk))

    # De-duplicate and return
    return list(dict.fromkeys(clauses))

class Command(BaseCommand):
    help = "Load OpenAI embeddings for a text file"

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str)
        parser.add_argument("--doc_id", type=str, required=True)

    def handle(self, *args, **options):
        filepath = options["filepath"]
        doc_id = options["doc_id"]

        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        print("📌 Running refined split_clauses() with ~KEY: extractor...")
        clauses = split_clauses(raw_text)
        print(f"🔍 Extracted {len(clauses)} clauses from: {filepath}")

        for clause in tqdm(clauses):
            if ClauseEmbedding.objects.filter(doc_id=doc_id, content=clause).exists():
                continue

            embedding = get_embedding(clause)
            ClauseEmbedding.objects.create(
                doc_id=doc_id,
                content=clause,
                embedding=embedding,
                length=len(clause)
            )

        print("✅ Embeddings loaded.")