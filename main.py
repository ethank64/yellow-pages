import os
import getpass
import json
import sys
from dotenv import load_dotenv

# Import necessary components from utils.py
from utils import read_and_simplify_schema, use_api

# LangChain components for RAG and Agent
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.agents import AgentExecutor, create_openai_tools_agent, Tool
from langchain.tools import StructuredTool
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage, AIMessage
from pydantic.v1 import BaseModel, Field, ValidationError # Import ValidationError for validation


# Load environment variables (for OpenAI API Key)
load_dotenv()

# Ensure OpenAI API key is set
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# --- Configuration ---
SCHEMA_FILE_PATH = "./sample_schema.json"
CHROMA_DB_DIRECTORY = "./chroma_db_agent_tools_v9" # Changed directory name for new run
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
LLM_MODEL_NAME = "gpt-4o-mini" 

# --- Global variable to hold the full simplified schema ---
ALL_SIMPLIFIED_SCHEMAS_DICT: dict[str, dict] = {} 

# Creates a LangChain tool from our propriety simplified schema format
def _create_langchain_tool_from_entry(simplified_op_entry: dict) -> Tool:
    """
    Converts a single simplified API operation entry into a LangChain Tool object.
    This function will be called dynamically for retrieved schema entries.
    """
    op_name = simplified_op_entry["name"]
    op_description = simplified_op_entry.get("summary", "")
    if not op_description:
        op_description = f"Calls the {op_name} API to retrieve information."

    # Create a Pydantic model for the tool's input parameters
    annotations = {}           # This will store the parameter names and their types
    field_definitions = {}     # This will store the parameter names and their descriptions

    # Iterate over the parameters in the simplified schema
    for param in simplified_op_entry.get("parameters", []):
        param_name = param["name"]
        param_type = str
        if param.get("type") == "integer":
            param_type = int
        elif param.get("type") == "boolean":
            param_type = bool
        elif param.get("type") == "number": 
            param_type = float
        
        field_description = param.get("description", f"The {param_name} parameter.")
        
        annotations[param_name] = param_type
        if param.get("required"):
            field_definitions[param_name] = Field(..., description=field_description)
        else:
            field_definitions[param_name] = Field(default=None, description=field_description)
            
    DynamicToolInput = type(
        f"{op_name.replace('.', '_').replace('-', '_')}Input",
        (BaseModel,),
        {'__annotations__': annotations, **field_definitions}
    )

    # --- FIX IS HERE: _tool_func now accepts **kwargs and manually validates with Pydantic ---
    def _tool_func(**kwargs) -> str: # Revert to **kwargs for broader compatibility with AgentExecutor dispatch
        # Manually validate incoming kwargs with the dynamically created Pydantic model
        validated_input = None
        try:
            validated_input = DynamicToolInput(**kwargs)
        except ValidationError as e:
            error_message = f"Pydantic Validation Error for tool '{op_name}': {e.errors()}"
            return error_message # Return validation error to the agent

        expected_params = simplified_op_entry.get("parameters", [])

        call_path_params = {}
        call_query_params = {}
        call_body_data = {}

        # Use the validated_input's dict representation for parameter separation
        input_dict_for_use_api = validated_input.dict()
        for param_def in expected_params:
            param_name = param_def["name"]
            # Check if parameter exists and is not None (for optional params)
            if param_name in input_dict_for_use_api and input_dict_for_use_api[param_name] is not None:
                if param_def.get("in") == "path":
                    call_path_params[param_name] = input_dict_for_use_api[param_name]
                elif param_def.get("in") == "query":
                    call_query_params[param_name] = input_dict_for_use_api[param_name]

        result = use_api( # Call your actual API utility from utils.py
            simplified_schema_entry=simplified_op_entry,
            path_params=call_path_params,
            query_params=call_query_params,
            body_data=call_body_data
        )
        return result

    return StructuredTool(
        name=op_name,
        description=op_description,
        func=_tool_func,
        args_schema=DynamicToolInput # The dynamically created Pydantic model defines its inputs
    )

# --- Step 1: Load and Process Simplified API Schemas into LangChain Documents for RAG ---
def load_schemas_as_rag_documents(file_path: str) -> list[Document]:
    """
    Loads OpenAPI schemas and converts them into LangChain Document objects for RAG.
    Also populates a global dictionary for quick lookup of full schema entries.
    """
    global ALL_SIMPLIFIED_SCHEMAS_DICT 
    simplified_schemas_list = read_and_simplify_schema(file_path)

    if not simplified_schemas_list:
        print("No simplified schemas loaded. Please check the schema file and its content.")
        return []

    ALL_SIMPLIFIED_SCHEMAS_DICT = {op['name']: op for op in simplified_schemas_list}

    documents = []
    for schema_entry in simplified_schemas_list:
        param_list_desc = ", ".join([f"{p['name']} ({p['type']}, {'required' if p['required'] else 'optional'})" 
                                      for p in schema_entry.get('parameters', [])])
        
        doc_content = (
            f"API Tool Name: {schema_entry.get('name')}\n"
            f"Description: {schema_entry.get('summary', 'No summary available.')}\n"
            f"Method: {schema_entry.get('method')}\n"
            f"URL Pattern: {schema_entry.get('url')}\n"
            f"Parameters: {param_list_desc if param_list_desc else 'None'}\n"
            f"Tags: {', '.join(schema_entry.get('tags', []))}\n"
        )
        documents.append(Document(page_content=doc_content, metadata={"operation_name": schema_entry.get("name")}))
    
    print(f"Loaded {len(documents)} API schema documents for RAG.")
    return documents

# --- Step 2: Initialize Embeddings and Vector Store (Chroma) ---
def setup_vector_store(documents: list[Document], db_directory: str) -> Chroma:
    """
    Initializes OpenAI embeddings and a Chroma vector store.
    Embeds documents and adds them to the vector store.
    """
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

    if os.path.exists(db_directory) and os.listdir(db_directory):
        vectorstore = Chroma(persist_directory=db_directory, embedding_function=embeddings)
    else:
        vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=db_directory)
        vectorstore.persist()
        print("ChromaDB created and persisted.")
    
    return vectorstore

# --- Step 3: Set up the Agent with Dynamic Tool Creation and Streaming (Logic for each turn) ---
def run_agent_turn_streaming(llm: ChatOpenAI, retriever: RunnablePassthrough, user_question: str, chat_history: list[BaseMessage]):
    """
    Runs the agent with streaming enabled to show real-time response generation.
    """
    # 1. Retrieve relevant schema documents based on the current query
    print("🔍 Retrieving relevant API tools...")
    relevant_docs = retriever.invoke(user_question)
    
    # 2. Dynamically create Tool objects for only these relevant schema entries
    dynamic_tools = []

    # Iterate over the relevant simplified schema entries
    for doc in relevant_docs:
        operation_name = doc.metadata.get('operation_name')
        if operation_name and operation_name in ALL_SIMPLIFIED_SCHEMAS_DICT:
            simplified_op_entry = ALL_SIMPLIFIED_SCHEMAS_DICT[operation_name]
            try:
                tool = _create_langchain_tool_from_entry(simplified_op_entry)
                dynamic_tools.append(tool)
            except Exception as e:
                print(f"Warning: Failed to dynamically create tool '{operation_name}': {e}")
        else:
            print(f"Warning: Retrieved document for '{operation_name}' but full schema entry not found in global dictionary or name is missing.")

    if not dynamic_tools:
        print("❌ No relevant API tools found.")
        return llm.invoke(f"I couldn't find any relevant API tools for your query: {user_question}. Please try rephrasing or asking something else.")

    print(f"✅ Found {len(dynamic_tools)} relevant API tools")

    # 3. Format the context string for the agent's prompt
    formatted_context = "\n---\n".join([doc.page_content for doc in relevant_docs])
    
    # 4. Create the agent for THIS turn with the dynamically generated tools
    agent = create_openai_tools_agent(llm, dynamic_tools, ChatPromptTemplate.from_messages([
        ("system", 
         "You are an AI assistant capable of answering questions by calling external API tools.\n"
         "When a user asks a question that requires API data, you must identify the appropriate tool to call.\n"
         "Look at the 'Relevant API Tools and Their Capabilities' below to decide which tool is best.\n"
         "If the information is not sufficient, state that you don't have enough information.\n"
         "Always respond in natural language unless explicitly asked for raw data.\n\n"
         "Relevant API Tools and Their Capabilities:\n{context}"
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]))

    # 5. Create the AgentExecutor for THIS turn
    agent_executor = AgentExecutor(
        agent=agent,
        tools=dynamic_tools, # Pass the dynamically created tools for this turn
        verbose=False,  # Set to False to avoid duplicate output during streaming
        handle_parsing_errors=True
    )

    try:
        print("\n🤖 AI Response:")
        print("=" * 50)
        
        # Use streaming for the agent executor
        full_response = ""
        for chunk in agent_executor.stream({
            "input": user_question,
            "chat_history": chat_history,
            "context": formatted_context # Pass context directly to prompt
        }):
            if "output" in chunk:
                output_chunk = chunk["output"]
                if isinstance(output_chunk, str):
                    print(output_chunk, end="", flush=True)
                    full_response += output_chunk
                else:
                    # Handle other output types
                    print(str(output_chunk), end="", flush=True)
                    full_response += str(output_chunk)
            elif "intermediate_steps" in chunk:
                # Show tool calls and their results
                for step in chunk["intermediate_steps"]:
                    if len(step) >= 2:
                        tool_name = step[0].tool
                        tool_result = step[1]
                        print(f"\n\n🔧 Tool Call: {tool_name}")
                        print(f"📊 Result: {tool_result}")
        
        print("\n" + "=" * 50)
        return full_response
        
    except Exception as e:
        error_msg = f"An internal error occurred while trying to process your request: {e}"
        print(f"\n❌ {error_msg}")
        return error_msg

# --- Main Execution Loop ---
def main():
    print("Starting API Agent with Dynamic Tool Creation and Streaming...")
    
    # Take the OpenAPI schema in the json file and convert them to the simplified schema format
    # Then, convert them to LangChain Document objects for RAG
    rag_documents = load_schemas_as_rag_documents(SCHEMA_FILE_PATH)
    
    if not rag_documents:
        print("No documents loaded. Exiting.")
        return

    # Embed the simplified schema
    vectorstore = setup_vector_store(rag_documents, CHROMA_DB_DIRECTORY)

    print("\nReady to interact with API tools!")
    print("Type 'exit' or 'quit' to end the session.")

    # Initialize basic RAG chatbot
    chat_history: list[BaseMessage] = []
    llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=0.0)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    while True:
        user_question = input("\nYour query: ")
        if user_question.lower() in ["exit", "quit"]:
            print("Exiting API Agent session.")
            break
        
        try:
            final_response_content = run_agent_turn_streaming(llm, retriever, user_question, chat_history)
            
            chat_history.append(HumanMessage(content=user_question))
            if isinstance(final_response_content, BaseMessage):
                chat_history.append(final_response_content)
            else:
                chat_history.append(AIMessage(content=str(final_response_content)))

        except Exception as e:
            print(f"\n[UNHANDLED EXCEPTION] An unhandled error occurred: {e}")
            print("Please try rephrasing your query or check the logs for more details.")
            chat_history.append(HumanMessage(content=user_question))
            chat_history.append(AIMessage(content=f"An unhandled error occurred: {e}"))


if __name__ == "__main__":
    if not os.path.exists(SCHEMA_FILE_PATH):
        print(f"Error: '{SCHEMA_FILE_PATH}' not found. Please ensure it's in the same directory.")
        print("You need to save the full OpenAPI JSON content (with 'servers' block) into this file.")
    else:
        main()