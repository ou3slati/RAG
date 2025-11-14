import readline
from dotenv import load_dotenv
load_dotenv()

from src.generator import RAGEngine

def main():
    print("Initializing RAG engine (index + embeddings + OpenAI client)...")
    rag = RAGEngine()

    print("\nType your question below. Type 'quit' to exit.\n")

    while True:
        q = input("Ask your RAG system> ").strip()
        if q.lower() in ("quit", "exit"):
            break
        if not q:
            continue

        # Decide output mode
        lower = q.lower()
        mode = "auto"
        output_name = "rag_output"

        if "pdf" in lower:
            mode = "pdf"
        if "cis320" in lower or "pset" in lower:
            mode = "cis320_pset"
            output_name = "cis320_pset"

        # Generate
        answer = rag.generate(q, mode=mode, output_name=output_name)
        print("\n--- Answer ---\n")
        print(answer)
        print("\n")


if __name__ == "__main__":
    main()
