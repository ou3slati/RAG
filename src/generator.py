import os
from dotenv import load_dotenv
from openai import OpenAI

from .retriever import Retriever
from .prompt_builder import build_prompt
from .pdf_generator import compile_pdf


class RAGEngine:
    def __init__(self):
        # Load environment
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")

        # OpenAI client
        self.client = OpenAI(api_key=api_key)

        # Retriever
        self.retriever = Retriever()

    def generate(self, query, mode="auto", k=5, output_name="rag_output"):
        """
        mode = auto | latex | pdf | cis320_pset | stat431_cheatsheet
        """

        # 1. Retrieve chunks
        chunks = self.retriever.retrieve(query, k=k)

        # 2. Build prompt
        system_prompt, user_prompt = build_prompt(query, chunks, mode=mode)

        # 3. LLM call
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        out = response.choices[0].message.content

        # 4. PDF mode
        if mode in ("pdf", "cis320_pset", "stat431_cheatsheet"):
            pdf_path = compile_pdf(out, output_name)
            return f"PDF generated: {pdf_path}"

        return out
