"""
MCP RAG: load existing Chroma + schema dict for discover (RAG only) and execute.
No LLM inside the MCP; the caller agent chooses which operation and params to use.
"""
import os
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from src.config import DEFAULT_CHROMA_DIR, DEFAULT_SCHEMA_PATH, EMBEDDING_MODEL_NAME
from src.utils import read_and_simplify_schema, use_api

ALL_SIMPLIFIED_SCHEMAS_DICT: dict[str, dict] = {}
_retriever = None


def init_rag(
    schema_path: Optional[str] = None,
    chroma_dir: Optional[str] = None,
    verbose: bool = False,
):
    """
    Load schema into ALL_SIMPLIFIED_SCHEMAS_DICT and open existing Chroma.
    Returns the retriever for discover(). Requires the Chroma directory to already exist (run indexer first).
    """
    global ALL_SIMPLIFIED_SCHEMAS_DICT
    schema_path = schema_path or os.environ.get("YELLOW_PAGES_SCHEMA_PATH", DEFAULT_SCHEMA_PATH)
    chroma_dir = chroma_dir or os.environ.get("YELLOW_PAGES_CHROMA_DIR", DEFAULT_CHROMA_DIR)

    simplified_schemas_list = read_and_simplify_schema(schema_path)
    if not simplified_schemas_list:
        raise FileNotFoundError(
            f"No schema documents loaded from {schema_path}. Check that the file exists and contains OpenAPI spec."
        )
    ALL_SIMPLIFIED_SCHEMAS_DICT = {op["name"]: op for op in simplified_schemas_list}

    if not os.path.exists(chroma_dir) or not os.listdir(chroma_dir):
        raise FileNotFoundError(
            f"Chroma directory not found or empty: {chroma_dir}. "
            "Run the indexer first: uv run python -m src.indexer"
        )

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = Chroma(persist_directory=chroma_dir, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
    return retriever


def ensure_rag():
    """Initialize the schema cache and retriever on demand."""
    global _retriever
    if _retriever is None:
        _retriever = init_rag(verbose=False)
    return _retriever


def discover(query: str, k: int = 5) -> list[dict]:
    """
    RAG only: retrieve operations relevant to the query. Returns a list of operation
    schema entries (operation_name, method, url, parameters, etc.) so the caller
    can choose which to run and with what params. No LLM; no execution.
    """
    retriever = ensure_rag()
    relevant_docs = retriever.invoke(query)
    if not relevant_docs:
        return []

    out = []
    seen = set()
    for doc in relevant_docs[:k]:
        op_name = doc.metadata.get("operation_name")
        if not op_name or op_name in seen:
            continue
        seen.add(op_name)
        entry = ALL_SIMPLIFIED_SCHEMAS_DICT.get(op_name)
        if entry:
            out.append(entry)
    return out


def execute(
    operation_name: str,
    path_params: Optional[dict] = None,
    query_params: Optional[dict] = None,
    body_data: Optional[dict] = None,
) -> str:
    """
    Execute one API operation by ID. Use operation_name from discover() and provide
    path_params, query_params, and optionally body_data as needed by the schema.
    """
    schema_entry = ALL_SIMPLIFIED_SCHEMAS_DICT.get(operation_name)
    if not schema_entry:
        return f"Unknown operation: {operation_name}. Call discover first to get valid operation names."
    return use_api(
        simplified_schema_entry=schema_entry,
        path_params=path_params or {},
        query_params=query_params or {},
        body_data=body_data or {},
    )


def set_retriever(retriever):
    global _retriever
    _retriever = retriever
