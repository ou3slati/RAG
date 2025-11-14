##RAG: Local Retrieval-Augmented Generation + LaTeX/PDF Synthesis

This project implements a fully local RAG pipeline over a personal knowledge base of LaTeX documents, homework sets, lecture notes, trading manuals, research writeups, and outlines. A query triggers semantic retrieval → LLM generation → LaTeX templating → PDF compilation. The system produces reproducible, high-quality typeset PDFs from natural-language prompts.

---

## Features

1. Vector Retrieval

* Embeddings: sentence-transformers/all-MiniLM-L6-v2
* Documents indexed from data/docs/
* Chunking + metadata mapping
* Top-K semantic search

2. OpenAI Generation

* Dynamic prompt construction from retrieved chunks, user profile, keywords, and query
* Supports all OpenAI-compatible clients
* Controlled, reproducible text generation

3. LaTeX/PDF Pipeline

* Dynamically builds LaTeX documents
* Assembles sections cleanly from model output
* Compiles PDFs via latexmk (BasicTeX-compatible)
* Outputs written to output/<slug>.pdf

4. Modular Code Architecture
   src/
   index_builder.py   – vector index creation
   retriever.py        – semantic search engine
   prompt_builder.py   – prompt assembly logic
   generator.py        – RAG engine controller
   pdf_utils.py        – LaTeX boilerplate + wrapping
   pdf_generator.py    – PDF compilation via latexmk

5. CLI Interface
   Interactive RAG shell:
   python3 run_rag.py

---

## Installation

1. Clone repository
   git clone [https://github.com/ou3slati/RAG.git](https://github.com/ou3slati/RAG.git)
   cd RAG

2. Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

3. Install LaTeX toolchain (macOS)
   brew install --cask basictex
   sudo tlmgr update --self
   sudo tlmgr install latexmk collection-latexrecommended collection-fontsrecommended

4. Set API key
   export OPENAI_API_KEY="sk-XXXX"

---

## Indexing Documents

Place .tex, .md, .txt, or .pdf files into:
data/docs/

Then build the index:
python3 -m src.index_builder

This creates:
index/rag.index
index/metadata.json

---

## Running the RAG Engine

Start interactive shell:
python3 run_rag.py

Example:
Ask your RAG system> generate a CIS 320 dynamic programming problem set
→ PDF generated in output/cis320_pset.pdf

---

## Repository Layout

data/docs/     – source documents to index
index/         – vector index and metadata (ignored in git)
output/        – generated PDFs (ignored)
src/           – retriever, generator, prompt builder, pdf engine
run_rag.py     – command-line interface
requirements.txt

---

## Common Use Cases

Academic

* CIS 320 dynamic programming practice problems
* STAT 430/431 midterm prep sheets
* Homework-style PDFs
* Lecture summaries reconstructed from notes

Research / ML

* GAN experiment interpretations
* Experiment logbook generation
* Math derivations and structured outlines

Professional

* Resume section generator
* Quant interview prep sheets
* Technical manuals

---

## Extending the System

Add more documents:
Place files in data/docs/ and rebuild index.

Modify domain keywords:
Edit DEFAULT_KEYWORDS in src/prompt_builder.py.

Customize LaTeX:
Edit templates in pdf_utils.py.

Swap embedding model:
Change EMBEDDING_MODEL in src/config.py.

---

## License

MIT License.
