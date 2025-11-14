from pathlib import Path
from .config import DOCS_DIR

def classify_doc_type(path):
    name = path.name.lower()

    # Global keyword → doc_type map
    KEYWORD_MAP = {
        # Core types
        "resume": "resume",
        "cv": "resume",
        "coverletter": "resume",
        "manual": "manual",
        "guide": "manual",

        # Homework / psets
        "hw": "pset",
        "homework": "pset",
        "pset": "pset",
        "problemset": "pset",
        "practice": "pset",
        "midterm": "pset",   # midterms are exam-like psets
        "exam": "pset",

        # Cheat sheets / outlines
        "cheat": "cheat_sheet",
        "godsheet": "cheat_sheet",
        "outline": "cheat_sheet",
        "summary": "cheat_sheet",

        # Courses — auto-map based on common patterns
        "cis320": "course_algorithms",
        "cis3200": "course_algorithms",
        "cis521": "course_ai",
        "cis545": "course_bigdata",
        "stat431": "course_statistics",

        # Quant & trading
        "quant": "quant_guide",
        "trading": "quant_guide",
        "superday": "quant_guide",

        # Research
        "gan": "research",
        "slingshot": "research",
        "ij": "research",
        "research": "research",
    }

    # Match any keyword inside the filename
    for keyword, dtype in KEYWORD_MAP.items():
        if keyword in name:
            return dtype

    return "unknown"

def parse_tex(path: Path):
    text = path.read_text(encoding="utf-8")
    if "\\begin{document}" not in text:
        return {"preamble": None, "sections": [text]}
    preamble, body = text.split("\\begin{document}", 1)
    return {"preamble": preamble, "body": body}

def split_sections(body: str):
    parts = body.split("\\section")
    sections = []
    for i, part in enumerate(parts):
        if i == 0:
            if part.strip():
                sections.append(part.strip())
            continue
        sections.append("\\section" + part)
    return [s.strip() for s in sections if len(s.strip()) > 0]

def main():
    for path in DOCS_DIR.iterdir():
        if not path.is_file():
            continue
        doc_type = classify_doc_type(path)
        print(f"=== {path.name} (doc_type={doc_type}) ===")
        if path.suffix == ".tex":
            parsed = parse_tex(path)
            preamble = parsed["preamble"]
            body = parsed.get("body", "")
            if preamble:
                print("  [preamble] length:", len(preamble))
            sections = split_sections(body)
            print("  [body sections]:", len(sections))
            for i, sec in enumerate(sections[:3]):
                snippet = sec[:120].replace("\n", " ")
                print(f"    Section {i}: {snippet}...")
        else:
            text = path.read_text(encoding="utf-8")
            print("  [meta txt] length:", len(text))

if __name__ == "__main__":
    main()
