import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from app.config import LLM_MODEL, EMBED_MODEL
from llama_index.core import Settings
from llama_index.core.schema import Document, TextNode
import torch

DATA_FOLDER = "./data"

Settings.embed_model = EMBED_MODEL
Settings.llm = LLM_MODEL

index = None
query_engine = None

def load_documents():
    """Read all documents in the DATA_FOLDER folder and return as a list of Documents."""
    nodes = SimpleDirectoryReader(DATA_FOLDER).load_data()
    
    documents = []
    for i, node in enumerate(nodes):
        print(f"Node {i}: {node}, Type: {type(node)}, Attributes: {dir(node)}")

        if isinstance(node, Document):
            documents.append(node)
        else:
            doc_id = getattr(node, "doc_id", None) or getattr(node, "id_", f"doc_{i+1}")
            documents.append(Document(text=node.text, doc_id=doc_id))

    return documents

def get_response(query):
    """Search for answers from indexed documents using a query engine."""
    if query_engine is None:
        raise ValueError("Query engine has not been initialized!")

    print(f"Received query: {query}")
    
    # Gunakan query engine untuk mendapatkan jawaban
    response = query_engine.query(query)

    # Debugging: Cek hasil query
    print(f"Response from query engine: {response}")

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return response

def initialize_index():
    """Initialize index with documents from DATA_FOLDER."""
    global index, query_engine  

    documents = load_documents()
    if documents:
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()

        if torch.cuda.is_available():
        torch.cuda.empty_cache()

initialize_index()

def add_document(file_path: str):
    """Adding a new document to the index from file_path."""
    global index, query_engine

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found!")

    new_nodes = SimpleDirectoryReader(input_files=[file_path]).load_data()
    
    new_docs = []
    for i, node in enumerate(new_nodes):
        print(f"DEBUG: Node {i}: {type(node)}, Attributes: {dir(node)}")  

        if isinstance(node, Document):
            new_docs.append(node)
        elif isinstance(node, TextNode):
            doc_id = getattr(node, "ref_doc_id", None) or f"new_doc_{i+1}"
            new_docs.append(Document(text=node.text, doc_id=doc_id))
        else:
            new_docs.append(Document(text=str(node), doc_id=f"new_doc_{i+1}"))

    print(f"DEBUG: Total documents to add: {len(new_docs)}")  
    
    if new_docs:
        try:
            index.add_documents(new_docs)
            query_engine = index.as_query_engine()

            print(f"DEBUG: Documents added to the index: {[doc.doc_id for doc in new_docs]}")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except AttributeError as e:
            print(f"ERROR: {e}") 
            raise

