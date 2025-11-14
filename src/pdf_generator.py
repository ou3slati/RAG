import subprocess
from pathlib import Path
import re


def clean_latex(latex: str) -> str:
    latex = re.sub(r"```.*?```", "", latex, flags=re.DOTALL)
    latex = latex.replace("```", "")
    latex = latex.replace("\r", "")
    return latex.strip()


def compile_pdf(latex_code: str, output_name: str = "rag_output"):
    latex_code = clean_latex(latex_code)

    outdir = Path("output")
    outdir.mkdir(exist_ok=True)

    tex_path = outdir / f"{output_name}.tex"
    pdf_path = outdir / f"{output_name}.pdf"

    tex_path.write_text(latex_code, encoding="utf-8")

    try:
        subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", tex_path.name],
            cwd=str(outdir),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError("LaTeX compilation failed:\n" + e.stderr.decode())

    return pdf_path
