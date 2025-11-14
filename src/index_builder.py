"""
Build a FAISS index over your LaTeX docs in data/docs.

Usage:
    python3 -m src.index_builder
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

import faiss  # from faiss-cpu
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import (
    DOCS_DIR,
    INDEX_PATH,
    METADATA_PATH,
    EMBED_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


# ---------- Helpers: LaTeX parsing / cleaning ----------

def read_tex(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def strip_comments(text: str) -> str:
    # Remove LaTeX comments (everything after % on a line)
    return re.sub(r"%.*", "", text)


def extract_body(text: str) -> str:
    # Keep content between \begin{document} and \end{document} if present
    start_match = re.search(r"\\begin\{document\}", text)
    end_match = re.search(r"\\end\{document\}", text)

    if start_match:
        start = start_match.end()
    else:
        start = 0

    if end_match:
        end = end_match.start()
    else:
        end = len(text)

    return text[start:end]


def latex_to_plain(text: str) -> str:
    """
    Very rough LaTeX → plain text stripper.
    Good enough for embeddings; we don't care about perfect formatting.
    """
    # Remove comments
    text = strip_comments(text)

    # Extract body
    text = extract_body(text)

    # Replace LaTeX newlines / spacing with spaces
    text = text.replace("~", " ")

    # Keep math content but drop $ signs
    text = text.replace("$$", " ")
    text = text.replace("$", " ")

    # Remove LaTeX commands like \command[opt]{arg} or \command{arg}
    text = re.sub(r"\\[a-zA-Z]+(\*?)\s*(\[[^\]]*\])?", " ", text)

    # Remove remaining braces (we just want words)
    text = text.replace("{", " ").replace("}", " ")

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------- Helpers: classification & tags ----------

def classify_doc_type(path: Path, plain_text: str) -> str:
    """
    Heuristic classification used for metadata.
    We don't need this to be perfect; it's for routing & labels.
    """
    name = path.name.lower()
    txt = plain_text.lower()

    # Cheat sheets / outlines / exam masters
    if any(w in name for w in ["cheat", "godsheet", "exam_master", "exam master"]):
        return "cheat_sheet"
    if any(w in name for w in ["outline", "master_outline", "study_outline"]):
        return "cheat_sheet"

    # Problem sets / homeworks
    if any(w in name for w in ["homework", "hw", "pset"]):
        return "pset"
    if "practice_midterm" in name or "practice midterm" in name:
        return "pset"
    if "midterm" in name or "quiz" in name or "exam" in name:
        return "pset"

    # Manuals / guides
    if any(w in name for w in ["manual", "guide", "handbook"]):
        return "manual"

    # Resume / CV
    if any(w in name for w in ["resume", "cv"]) or "coverletter" in name:
        return "resume"

    # Research notes / papers
    if any(w in name for w in ["gan_", "slingshot", "ij_", "research"]):
        return "research"

    # Course notes
    if "notes" in name:
        return "course_notes"

    # Fallback heuristic by contents
    if "generative adversarial network" in txt or "gan" in txt:
        return "research"
    if "hypothesis testing" in txt or "confidence interval" in txt:
        return "course_statistics"

    return "unknown"


def infer_tags(path: Path, doc_type: str) -> List[str]:
    """
    Tags per document; chunks inherit these. Used for keyword routing.
    """
    name = path.name.lower()
    tags = {doc_type}

    # Course markers
    for course_tag in ["cis320", "cis5210", "cis5450", "stat431", "wharton3010"]:
        if course_tag in name:
            tags.add(course_tag)

    # Keyword-style tags that match KEYWORD_GROUPS
    if any(w in name for w in ["resume", "cv"]):
        tags.add("resume")
    if any(w in name for w in ["manual", "guide", "handbook"]):
        tags.add("manual")
    if any(w in name for w in ["homework", "hw", "pset"]):
        tags.add("hw")
    if any(w in name for w in ["cheat", "godsheet", "exam master", "study_outline"]):
        tags.add("cheat_sheet")

    # Trading / quant docs
    if "trading" in name or "quant" in name:
        tags.add("trading")

    return sorted(tags)


# ---------- Helpers: chunking ----------

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    n = len(text)
    if n == 0:
        return chunks

    step = max(1, chunk_size - overlap)
    start = 0
    while start < n:
        end = min(n, start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(
                {
                    "start": start,
                    "end": end,
                    "text": chunk,
                }
            )
        start += step

    return chunks


# ---------- Main indexing logic ----------

def build_index() -> None:
    print(f"Scanning LaTeX docs in: {DOCS_DIR}")
    tex_paths = sorted(DOCS_DIR.glob("*.tex"))
    if not tex_paths:
        raise RuntimeError(f"No .tex files found in {DOCS_DIR}")

    all_chunks: List[Dict[str, Any]] = []

    # 1) Parse and chunk
    for doc_id, path in enumerate(tex_paths):
        print(f"Parsing {path.name} ...")
        raw = read_tex(path)
        plain = latex_to_plain(raw)
        doc_type = classify_doc_type(path, plain)
        tags = infer_tags(path, doc_type)

        doc_chunks = chunk_text(plain, CHUNK_SIZE, CHUNK_OVERLAP)
        print(f"  -> {len(doc_chunks)} chunks, type={doc_type}, tags={tags}")

        for chunk_idx, ch in enumerate(doc_chunks):
            all_chunks.append(
                {
                    "id": len(all_chunks),
                    "doc_id": doc_id,
                    "doc_path": str(path.relative_to(DOCS_DIR)),
                    "doc_name": path.name,
                    "doc_type": doc_type,
                    "tags": tags,
                    "chunk_index": chunk_idx,
                    "start": ch["start"],
                    "end": ch["end"],
                    "text": ch["text"],
                }
            )

    if not all_chunks:
        raise RuntimeError("No chunks produced; check chunking / docs.")

    print(f"Total chunks: {len(all_chunks)}")

    # 2) Embeddings
    print("Loading embedding model:", EMBED_MODEL_NAME)
    model = SentenceTransformer(EMBED_MODEL_NAME)

    texts = [c["text"] for c in all_chunks]
    print("Embedding chunks...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    # 3) Build FAISS index
    dim = embeddings.shape[1]
    print(f"Building FAISS index (dim={dim})...")
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # 4) Save index + metadata
    print("Saving index & metadata...")
    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(
        json.dumps(all_chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("✔️ Index built successfully!")
    print(f"  Index:    {INDEX_PATH}")
    print(f"  Metadata: {METADATA_PATH}")


if __name__ == "__main__":
    build_index()
