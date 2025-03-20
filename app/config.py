from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings 
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

dotenv_path = "C:/Grader/chatbot-rag/.env" 
load_dotenv(dotenv_path)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print(f"Token from .env: {HUGGINGFACEHUB_API_TOKEN}")  

if not HUGGINGFACEHUB_API_TOKEN or not HUGGINGFACEHUB_API_TOKEN.startswith("hf_"):
    raise ValueError("Hugging Face API token is invalid or has not been set.")

LLM_MODEL = HuggingFaceInferenceAPI(
    model_name="mistralai/Mistral-7B-Instruct-v0.3",
    api_url="https://api-inference.huggingface.co/v1/chat/completions",
    api_key=HUGGINGFACEHUB_API_TOKEN
)

EMBED_MODEL = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.embed_model = EMBED_MODEL 