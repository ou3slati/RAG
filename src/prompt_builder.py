from typing import List, Dict, Tuple


def _infer_style(query: str, chunks: List[Dict]) -> str:
    q = query.lower()

    tags = set()
    doc_types = set()
    for ch in chunks:
        for t in ch.get("tags", []):
            tags.add(str(t).lower())
        if ch.get("doc_type"):
            doc_types.add(ch["doc_type"].lower())

    # CIS320
    if "cis320" in q or "cis 320" in q or "cis320" in tags:
        if ("pset" in q or "problem set" in q or "hw" in q or "pset" in tags):
            return "cis320_pset"
        return "cis320_notes"

    # STAT431
    if "stat431" in q or "cheat" in q:
        return "stat431_cheatsheet"

    return "generic"


def _build_context_snippets(chunks: List[Dict], max_chunks: int = 10, max_chars: int = 900) -> str:
    rows = []
    for ch in chunks[:max_chunks]:
        text = (ch.get("text") or "").strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        meta = []
        if ch.get("doc_type"):
            meta.append("type=" + ch["doc_type"])
        if ch.get("tags"):
            meta.append("tags=" + ",".join(ch["tags"]))
        header = " | ".join(meta) if meta else "chunk"

        rows.append(f"--- [{header}]\n{text}")

    return "\n\n".join(rows)


def build_prompt(query: str, chunks: List[Dict], mode: str = "auto") -> Tuple[str, str]:
    if mode == "auto":
        style = _infer_style(query, chunks)
    else:
        style = mode

    context = _build_context_snippets(chunks)

    # ---------- CIS 320 PSET ----------
    if style == "cis320_pset":
        system_prompt = r"""
You generate CIS 320 dynamic programming problem sets in strict LaTeX.

Rules:
- Output ONLY raw LaTeX (no markdown).
- Start with \documentclass{article}.
- Use Amine's style: title, author, maketitle, sections.
- Provide 3–5 dynamic programming problems with subparts.
- NO solutions.
"""
        user_prompt = f"{query}\n\nContext:\n{context}"
        return system_prompt, user_prompt

    # ---------- STAT 431 Cheat sheet ----------
    if style == "stat431_cheatsheet":
        system_prompt = r"""
You generate STAT 431 cheat sheets in compact LaTeX.
ONLY raw LaTeX output.
"""
        user_prompt = f"{query}\n\nContext:\n{context}"
        return system_prompt, user_prompt

    # ---------- generic ----------
    system_prompt = "Use context to answer the user's question."
    user_prompt = f"Query: {query}\n\nContext:\n{context}"
    return system_prompt, user_prompt
