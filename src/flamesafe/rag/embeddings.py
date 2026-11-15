"""Explicit model acquisition; runtime never downloads weights."""

import re


class LocalEmbeddings:
    def __init__(self, settings, allow_download=False):
        from sentence_transformers import SentenceTransformer

        revision = settings.embedding_revision
        if not re.fullmatch(r"[a-f0-9]{40}", revision):
            raise ValueError("Set embeddings.revision to an immutable 40-character commit SHA.")
        if allow_download:
            from huggingface_hub import snapshot_download

            snapshot_download(
                repo_id=settings.embedding_model,
                revision=revision,
                local_dir=settings.embedding_path,
                ignore_patterns=["onnx/*", "openvino/*", "*.bin"],
            )
            (settings.embedding_path / "flamesafe_revision.txt").write_text(revision)
        marker = settings.embedding_path / "flamesafe_revision.txt"
        if not marker.exists() or marker.read_text().strip() != revision:
            raise ValueError("Local model revision missing/mismatched; explicit download required.")
        self.model = SentenceTransformer(
            str(settings.embedding_path), local_files_only=True, trust_remote_code=False
        )

    def count(self, text):
        return len(self.model.tokenizer.encode("passage: " + text, add_special_tokens=True))

    def encode(self, texts, query=False):
        prefix = "query: " if query else "passage: "
        for text in texts:
            if len(self.model.tokenizer.encode(prefix + text)) > 512:
                raise ValueError("Embedding input exceeds 512 tokens; no silent truncation.")
        return self.model.encode(
            [prefix + text for text in texts], normalize_embeddings=True
        ).tolist()
