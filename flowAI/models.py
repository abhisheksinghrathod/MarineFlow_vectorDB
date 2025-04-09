# flowAI/models.py
from django.db import models
from pgvector.django import VectorField

class ClauseEmbedding(models.Model):
    doc_id = models.CharField(max_length=100)         # e.g. vessel, file ID
    source_type = models.CharField(max_length=10)     # "recap" or "sof"
    content = models.TextField()                      # clause/paragraph content
    embedding = VectorField(dimensions=1536)          # using text-embedding-3-small
    created_at = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField(default=0)

    class Meta:
        db_table = "clause_embedding"

    def __str__(self):
        return f"{self.doc_id} [{self.source_type}]"

