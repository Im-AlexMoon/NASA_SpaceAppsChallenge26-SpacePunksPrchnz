"""BM25 + dense reciprocal rank fusion; explicit lexical development mode."""

import re
import threading
import unicodedata

import numpy as np
from rank_bm25 import BM25Okapi

from flamesafe.rag.index import load_records, validate

ALIASES = {
    "ignicion": "ignition",
    "quemado": "burn",
    "duracion": "time",
    "oxigeno": "oxygen",
    "nitrogeno": "nitrogen",
    "caudal": "flow",
    "presion": "pressure",
    "llama": "flame",
    "combustible": "fuel",
    "gotas": "droplet",
    "origen": "origin",
}


def tokens(text):
    text = "".join(
        c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c)
    )
    words = re.findall(r"[\w-]+", text)
    return words + [ALIASES[word] for word in words if word in ALIASES]


class Retriever:
    def __init__(self, bundle, settings):
        self.manifest = validate(bundle)
        self.sources, self.chunks = load_records(bundle)
        self.bm25 = BM25Okapi([tokens(chunk.text) for chunk in self.chunks])
        self.encoder = self.table = None
        self.lock = threading.Lock()
        if self.manifest.retrieval_mode == "hybrid":
            import lancedb

            from flamesafe.rag.embeddings import LocalEmbeddings

            if self.manifest.embedding_revision != settings.embedding_revision:
                raise ValueError("Embedding revision differs from index.")
            self.encoder = LocalEmbeddings(settings)
            self.table = lancedb.connect(str(bundle / "vectors")).open_table("chunks")

    def search(self, question, top_k=8):
        scores = self.bm25.get_scores(tokens(question))
        lexical = [
            self.chunks[i].chunk_id
            for i in np.argsort(-scores, kind="stable")[:30]
            if scores[i] > 0
        ]
        rankings = [lexical]
        if self.encoder:
            with self.lock:
                vector = self.encoder.encode([question], query=True)[0]
            rankings.append(
                [row["chunk_id"] for row in self.table.search(vector).limit(30).to_list()]
            )
        fused = {}
        for ranking in rankings:
            for rank, chunk_id in enumerate(ranking, 1):
                fused[chunk_id] = fused.get(chunk_id, 0) + 1 / (60 + rank)
        by_id = {chunk.chunk_id: chunk for chunk in self.chunks}
        identifiers = set(re.findall(r"\b[a-z][a-z0-9]*_[a-z0-9_]+\b|PSI-\d+", question, re.I))
        for chunk in self.chunks:
            if identifiers and any(
                re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", chunk.text, re.I)
                for word in identifiers
            ):
                fused[chunk.chunk_id] = fused.get(chunk.chunk_id, 0) + 1 / 30
        result, per_source = [], {}
        for chunk_id in sorted(fused, key=lambda key: (-fused[key], key)):
            chunk = by_id[chunk_id]
            if per_source.get(chunk.source_id, 0) >= 2:
                continue
            result.append(chunk)
            per_source[chunk.source_id] = per_source.get(chunk.source_id, 0) + 1
            if len(result) >= top_k:
                break
        return result
