from pathlib import Path

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
PROFILE_DIR = DATA_DIR / "profile"

INDEX_DIR = BASE_DIR / "index"
INDEX_PATH = INDEX_DIR / "rag.index"
METADATA_PATH = INDEX_DIR / "metadata.json"

PROFILE_PATH = PROFILE_DIR / "user_profile.txt"

# Make sure index dir exists
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# === Models ===
# Sentence-transformers model for embeddings
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# OpenAI model for generation
# You can switch this to "gpt-4.1" / "gpt-4.1-mini" / "o3-mini" etc.
DEFAULT_MODEL_NAME = "gpt-4.1-mini"

# === Chunking parameters ===
CHUNK_SIZE = 700       # characters
CHUNK_OVERLAP = 150    # characters

# === Keyword routing ===
# Canonical keyword -> list of query triggers
# You can edit / extend this easily.
KEYWORD_GROUPS = {
    "resume": [
        "resume", "cv", "curriculum vitae", "cover letter",
        "application letter", "proprietary trading intern application",
    ],
    "manual": [
        "manual", "guide", "handbook", "playbook", "godsheet",
        "trading manual", "developer manual",
    ],
    "hw": [
        "hw", "homework", "pset", "problem set", "assignment",
    ],
    "cheat_sheet": [
        "cheat sheet", "cheatsheet", "godsheet", "exam master",
        "study outline", "warmup", "drill set", "practice midterm",
    ],
}
