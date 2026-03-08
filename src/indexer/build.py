"""
Build Chroma vector store from OpenAPI schema.
Run once (or when schema changes). No LLM, no MCP.
"""
import os
import shutil
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.config import DEFAULT_CHROMA_DIR, DEFAULT_SCHEMA_PATH, EMBEDDING_MODEL_NAME
from src.utils import read_and_simplify_schema


def chroma_db_exists(chroma_dir: str) -> bool:
    """Return True if chroma_dir exists and looks like a Chroma persist directory."""
    if not os.path.isdir(chroma_dir):
        return False
    # Chroma persists at least chroma.sqlite3
    return os.path.isfile(os.path.join(chroma_dir, "chroma.sqlite3"))


def _simplified_to_documents(simplified_schemas_list: list) -> list[Document]:
    """Convert simplified schema list to LangChain Documents for RAG."""
    documents = []
    for schema_entry in simplified_schemas_list:
        param_list_desc = ", ".join(
            [
                f"{p['name']} ({p['type']}, {'required' if p['required'] else 'optional'})"
                for p in schema_entry.get("parameters", [])
            ]
        )
        doc_content = (
            f"API Tool Name: {schema_entry.get('name')}\n"
            f"Description: {schema_entry.get('summary', 'No summary available.')}\n"
            f"Method: {schema_entry.get('method')}\n"
            f"URL Pattern: {schema_entry.get('url')}\n"
            f"Parameters: {param_list_desc if param_list_desc else 'None'}\n"
            f"Tags: {', '.join(schema_entry.get('tags', []))}\n"
        )
        documents.append(
            Document(page_content=doc_content, metadata={"operation_name": schema_entry.get("name")})
        )
    return documents


def run(
    schema_path: Optional[str] = None,
    chroma_dir: Optional[str] = None,
    verbose: bool = True,
) -> None:
    """
    Load schema, build documents, create Chroma from documents and persist.
    Always (re)builds; use env YELLOW_PAGES_SCHEMA_PATH, YELLOW_PAGES_CHROMA_DIR to override paths.
    """
    schema_path = schema_path or os.environ.get("YELLOW_PAGES_SCHEMA_PATH", DEFAULT_SCHEMA_PATH)
    chroma_dir = chroma_dir or os.environ.get("YELLOW_PAGES_CHROMA_DIR", DEFAULT_CHROMA_DIR)

    simplified_schemas_list = read_and_simplify_schema(schema_path)
    if not simplified_schemas_list:
        raise FileNotFoundError(
            f"No simplified schemas loaded from {schema_path}. Check that the file exists and contains OpenAPI spec."
        )

    documents = _simplified_to_documents(simplified_schemas_list)
    if verbose:
        print(f"Loaded {len(documents)} API schema documents for indexing.")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = Chroma.from_documents(
        documents, embeddings, persist_directory=chroma_dir
    )
    vectorstore.persist()
    if verbose:
        print("ChromaDB created and persisted.")


def run_create(
    schema_path: Optional[str] = None,
    chroma_dir: Optional[str] = None,
    verbose: bool = True,
) -> None:
    """
    Create Chroma DB and embed tools only if it does not already exist.
    """
    chroma_dir = chroma_dir or os.environ.get("YELLOW_PAGES_CHROMA_DIR", DEFAULT_CHROMA_DIR)
    if chroma_db_exists(chroma_dir):
        if verbose:
            print(f"Chroma DB already exists at {chroma_dir}. Use reset-db to rebuild or update-db to add new tools.")
        return
    run(schema_path=schema_path, chroma_dir=chroma_dir, verbose=verbose)


def run_reset(
    schema_path: Optional[str] = None,
    chroma_dir: Optional[str] = None,
    verbose: bool = True,
) -> None:
    """
    Remove existing Chroma DB (if any), then create it fresh and embed all tools.
    """
    chroma_dir = chroma_dir or os.environ.get("YELLOW_PAGES_CHROMA_DIR", DEFAULT_CHROMA_DIR)
    if os.path.isdir(chroma_dir):
        shutil.rmtree(chroma_dir)
        if verbose:
            print(f"Removed existing Chroma DB at {chroma_dir}.")
    run(schema_path=schema_path, chroma_dir=chroma_dir, verbose=verbose)


def run_update(
    schema_path: Optional[str] = None,
    chroma_dir: Optional[str] = None,
    verbose: bool = True,
) -> None:
    """
    Embed only new tools from the schema and append them to the existing Chroma DB.
    Existing operations are left unchanged.
    """
    schema_path = schema_path or os.environ.get("YELLOW_PAGES_SCHEMA_PATH", DEFAULT_SCHEMA_PATH)
    chroma_dir = chroma_dir or os.environ.get("YELLOW_PAGES_CHROMA_DIR", DEFAULT_CHROMA_DIR)

    if not chroma_db_exists(chroma_dir):
        if verbose:
            print(f"No existing Chroma DB at {chroma_dir}. Creating from scratch.")
        run(schema_path=schema_path, chroma_dir=chroma_dir, verbose=verbose)
        return

    simplified_schemas_list = read_and_simplify_schema(schema_path)
    if not simplified_schemas_list:
        raise FileNotFoundError(
            f"No simplified schemas loaded from {schema_path}. Check that the file exists and contains OpenAPI spec."
        )

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = Chroma(persist_directory=chroma_dir, embedding_function=embeddings)

    result = vectorstore.get(include=["metadatas"])
    existing_ops = set()
    for m in result.get("metadatas") or []:
        if m and m.get("operation_name"):
            existing_ops.add(m["operation_name"])

    new_schemas = [s for s in simplified_schemas_list if s.get("name") not in existing_ops]
    if not new_schemas:
        if verbose:
            print("No new tools to embed. DB is up to date.")
        return

    new_documents = _simplified_to_documents(new_schemas)
    vectorstore.add_documents(new_documents)
    vectorstore.persist()
    if verbose:
        print(f"Added {len(new_documents)} new tool(s) to Chroma DB.")
