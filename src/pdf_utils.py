"""
Helper functions to go from LaTeX string -> PDF file, using pdflatex.

You don't HAVE to use this right now; but it's wired so you can easily
add a 'generate_pdf' path later.
"""

import subprocess
from pathlib import Path


def ensure_full_document(body_tex: str) -> str:
    """
    If the LaTeX already contains \\documentclass, return it as-is.
    Otherwise, wrap in a minimal article preamble.
    """
    if "\\documentclass" in body_tex:
        return body_tex

    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb,amsthm,mathtools}
\usepackage{enumitem}
\usepackage{hyperref}

\begin{document}
""" + body_tex + "\n\\end{document}\n"


def tex_to_pdf(
    tex_source: str,
    output_dir: Path,
    basename: str = "rag_output",
) -> Path:
    """
    Write tex_source to output_dir/basename.tex and run pdflatex.
    Returns the path to the resulting PDF.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tex_path = output_dir / f"{basename}.tex"
    tex_path.write_text(tex_source, encoding="utf-8")

    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        tex_path.name,
    ]
    try:
        subprocess.run(
            cmd,
            cwd=output_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
    except Exception as e:
        raise RuntimeError(f"pdflatex failed: {e}")

    pdf_path = output_dir / f"{basename}.pdf"
    if not pdf_path.exists():
        raise RuntimeError(f"Expected PDF not found at {pdf_path}")
    return pdf_path
