import os
import shutil
import requests
import time
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status, Header
from pydantic import BaseModel
from app.config import supabase
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from app.model import add_document, DATA_FOLDER, get_response
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not HF_TOKEN:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN not found. Make sure it is in .env!")

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
print("TOKEN:", HF_TOKEN[:10] + "")  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SUPABASE_JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("SUPABASE_JWT_SECRET not found. Make sure it's in .env!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class AuthRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str

class QueryRequest(BaseModel):
    question: str


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded Token Payload:", payload)  
        email: str = payload.get("email")  
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token: No email found")
        return {"email": email}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_access_token(email: str, expires_delta: timedelta | None = None):
    to_encode = {"email": email}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def query_huggingface(prompt):
    """Sending a request to the Hugging Face API model"""
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200, "temperature": 0.7}}
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status() 
        
        json_response = response.json()
        if isinstance(json_response, list) and "generated_text" in json_response[0]:
            return json_response[0]["generated_text"]
        else:
            raise ValueError(f"Incorrect response format:{json_response}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {str(e)}")
    except ValueError as e:
        raise Exception(f"Parsing error: {str(e)}")

@app.post("/token", response_model=AuthResponse)
async def login_for_access_token(request: AuthRequest):
    try:
        user = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        access_token = create_access_token({"sub": request.email}) 
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials or error: {str(e)}")


@app.post("/register", response_model=AuthResponse)
async def register(request: AuthRequest):
    """Endpoint for new user registration."""
    try:
        user = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
    
        access_token = user.session.access_token

        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error during registration: {str(e)}")



@app.get("/")
def home():
    return {"message": "API is running!"} 

@app.post("/query")
def query_from_hf(request: QueryRequest, token: dict = Depends(verify_token)):
    try:
        response = query_huggingface(request.question)

        if response.lower().startswith(request.question.lower()):
            response = response[len(request.question):].strip()

        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    try:
        os.makedirs(DATA_FOLDER, exist_ok=True)

        file_path = os.path.join(DATA_FOLDER, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        

        add_document(file_path)
    
        return {"message": f"File {file.filename} successfully uploaded and processed."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while ingesting file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)