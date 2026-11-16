"""Allowlisted metadata, dictionary rows and explicitly reviewed documents."""

import re

import pandas as pd
import yaml

from flamesafe import config
from flamesafe.rag.chunking import sections, split_text
from flamesafe.rag.schemas import DocumentChunk, SourceRecord
from flamesafe.rag.utils import digest, file_hash


def build_corpus(investigations, count, registry_path=None):
    registry_path = registry_path or config.CONFIG_DIR / "rag_sources.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    sources, chunks, definitions, hashes = [], [], [], {}

    def add(source, heading, text, language=None):
        if not text.strip():
            return
        if not any(s.source_id == source.source_id for s in sources):
            sources.append(source)
        prefix = f"{source.title}\n{heading}\n"
        budget = 384 - count(prefix)
        if budget < 40:
            raise ValueError("Source heading too long; curate it.")
        for part in split_text(text, count, budget):
            body = prefix + part
            chunks.append(
                DocumentChunk(
                    chunk_id="chunk-" + digest([source.source_id, heading, body]),
                    source_id=source.source_id,
                    text=body,
                    section=heading,
                    token_count=count(body),
                    language=language or source.language,
                )
            )

    for _, row in investigations.iterrows():
        psi = str(row["psi_id"])
        for field in registry["catalog_fields"]:
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                continue
            source = SourceRecord(
                source_id=f"psi-{psi}-{field}",
                title=f"{psi}: {row['title']}",
                source_type="psi_metadata",
                sha256=digest(value),
                locator=f"investigations/{psi}/{field}",
                psi_ids=[psi],
                language="en",
                license_or_terms=str(row.get("license_name") or "See PSI source"),
            )
            add(source, field, value)
    path = (config.ROOT / registry["dictionary"]).resolve()
    path.relative_to(config.ROOT)
    hashes[registry["dictionary"]] = file_hash(path)
    table = None
    in_gold = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_gold = line.strip() == "## Gold"
            table = None
        if not in_gold:
            continue
        match = re.match(
            r"### `(gas_flame_tests|droplet_tests|droplet_reference_points|investigations|publications)`",
            line,
        )
        if line.startswith("###"):
            table = match[1] if match else None
        if table and line.startswith("| `"):
            match = re.match(r"\| `([^`]+)`", line)
            if not match:
                continue
            sid = f"dictionary-{table}-{digest(line)[:16]}"
            source = SourceRecord(
                source_id=sid,
                title=f"{table}: {match[1]}",
                source_type="dictionary",
                sha256=digest(line),
                locator=f"{registry['dictionary']}#{table}",
                language="es",
                review_status="repository_definition",
                license_or_terms="Repository license",
            )
            add(
                source,
                "Column | Type | Unit | Origin | Transformation | Evidence | Nullable | Notes",
                line,
            )
            for variable in re.findall(r"`([^`]+)`", line.split("|")[1]):
                definitions.append(
                    {
                        "variable": variable.strip(),
                        "table_name": table,
                        "definition": line,
                        "source_id": sid,
                    }
                )
    publication = config.publication()
    findings_path = config.ROOT / publication["findings"]["source"]
    finding_status = {entry["id"]: entry["status"] for entry in yaml.safe_load(
        findings_path.read_text(encoding="utf-8")
    )["findings"]} if publication["findings"]["enabled"] else {}
    hashes["configs/publication.yaml"] = file_hash(config.CONFIG_DIR / "publication.yaml")
    for item in registry.get("documents", []):
        if any(not publication[key]["enabled"] or publication[key]["status"] != "reviewed"
               for key in item.get("publication_blocks", [])):
            continue
        path = (config.ROOT / item["path"]).resolve()
        path.relative_to(config.ROOT)
        if path.stem in finding_status and finding_status[path.stem] != "reviewed":
            continue
        if path.stem == "STUDY_SUMMARY" and any(status != "reviewed" for status in finding_status.values()):
            continue
        if path.name.startswith("_") or path.suffix.lower() not in {".md", ".pdf"}:
            raise ValueError("Only curated Markdown/PDF sources are allowed.")
        if (
            not item.get("allow_provider")
            or not item.get("reviewed_by")
            or not item.get("license_or_terms")
        ):
            raise ValueError("Document requires reviewer, rights and provider eligibility.")
        actual = file_hash(path)
        if actual != item.get("sha256"):
            raise ValueError("Document hash changed; review must be renewed.")
        hashes[item["path"]] = actual
        source = SourceRecord(
            source_id="doc-" + actual,
            title=item.get("title", path.stem),
            source_type="reviewed_document",
            sha256=actual,
            locator=item["path"],
            language=item.get("language", "es"),
            review_status="reviewed",
            reviewed_by=item["reviewed_by"],
            license_or_terms=item["license_or_terms"],
        )
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader

            parts = [
                (f"page:{i + 1}", page.extract_text() or "")
                for i, page in enumerate(PdfReader(path).pages)
            ]
        else:
            parts = list(sections(path.read_text(encoding="utf-8")))
        selected = set(item.get("approved_sections", []))
        if not selected or not selected.issubset({heading for heading, _ in parts}):
            raise ValueError("Missing or invalid approved_sections.")
        for heading, text in parts:
            if heading in selected:
                if not text.strip():
                    raise ValueError("Empty extraction; OCR/curation required.")
                add(source, heading, text, item.get("section_languages", {}).get(heading))
    chunks = list({chunk.chunk_id: chunk for chunk in chunks}.values())
    return sources, chunks, pd.DataFrame(definitions), hashes
