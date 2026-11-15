"""Bounded chunks retaining table context."""

import re


def sections(text):
    heading, lines = "Introduction", []
    for line in text.splitlines():
        if line.startswith("#"):
            if lines:
                yield heading, "\n".join(lines).strip()
            heading, lines = line.lstrip("# "), []
        else:
            lines.append(line)
    if lines:
        yield heading, "\n".join(lines).strip()


def split_text(text, count, limit=384):
    buffer, header = [], []
    for line in text.splitlines():
        if not line.strip():
            continue
        if re.match(r"\|\s*:?-", line) and buffer:
            header = [buffer[-1], line]
        if not line.startswith("|"):
            header = []
        if count(line) > limit:
            if line.startswith("|"):
                raise ValueError("Oversized table row requires curation.")
            if buffer:
                yield "\n".join(buffer)
                buffer = []
            piece = []
            for word in line.split():
                if count(word) > limit:
                    raise ValueError("Oversized token requires curation.")
                if count(" ".join([*piece, word])) > limit:
                    yield " ".join(piece)
                    piece = []
                piece.append(word)
            buffer = [" ".join(piece)] if piece else []
        elif count("\n".join([*buffer, line])) > limit:
            yield "\n".join(buffer)
            buffer = [*header, line] if header else [line]
            if count("\n".join(buffer)) > limit:
                raise ValueError("Table header and row exceed token budget.")
        else:
            buffer.append(line)
    if buffer:
        yield "\n".join(buffer)
