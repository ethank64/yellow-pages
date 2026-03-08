"""Shared env-based config for indexer and MCP."""
import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_SCHEMA_PATH = "./sample_schema.json"
DEFAULT_CHROMA_DIR = "./chroma_db_agent_tools_v9"
EMBEDDING_MODEL_NAME = os.environ.get(
    "YELLOW_PAGES_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
