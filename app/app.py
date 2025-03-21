import os
import shutil
import requests
import time
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from pydantic import BaseModel
from app.config import supabase
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from app.model import add_document, DATA_FOLDER, get_response



# Load environment variables
load_dotenv(override=True)

# API Hugging Face
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not HF_TOKEN:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN tidak ditemukan. Pastikan sudah ada di .env!")

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}

# Debugging token (hapus jika tidak diperlukan)
print("TOKEN:", HF_TOKEN[:10] + "")  # Cuma nampilin sebagian token biar aman

try:
    response = supabase.table("users").select("*").limit(1).execute()
    print("Koneksi ke Supabase berhasil:", response)
except Exception as e:
    print("Gagal koneksi ke Supabase:", e)

# FastAPI instance
app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SUPABASE_JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("SUPABASE_JWT_SECRET tidak ditemukan. Pastikan sudah ada di .env!")

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
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token: No subject (sub)")
        return {"email": email}  # Return email pengguna dari token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "sub": data.get("email")})  # Tambahkan email
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def query_huggingface(prompt):
    """Mengirim permintaan ke model Hugging Face API"""
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200, "temperature": 0.7}}
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # Akan raise error jika status bukan 2xx
        
        json_response = response.json()
        if isinstance(json_response, list) and "generated_text" in json_response[0]:
            return json_response[0]["generated_text"]
        else:
            raise ValueError(f"Format respons tidak sesuai: {json_response}")

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

        access_token = create_access_token({"sub": request.email})  # Buat token JWT sendiri
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials or error: {str(e)}")


@app.post("/register", response_model=AuthResponse)
async def register(request: AuthRequest):
    """Endpoint untuk registrasi pengguna baru."""
    try:
        # Supabase register user
        user = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        # Ambil token dari response
        access_token = user.session.access_token

        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saat registrasi: {str(e)}")


@app.post("/login", response_model=AuthResponse)
async def login(request: AuthRequest):
    try:
        start_time = time.time()
        user = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        elapsed_time = time.time() - start_time
        print(f"Login sukses dalam {elapsed_time:.2f} detik")

        return {"access_token": user.session.access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials or error: {str(e)}")

@app.get("/")
def home():
    return {"message": "API is running!"} 

# # Endpoint untuk query dari dokumen
# @app.post("/query_from_docs")
# def query_from_docs(request: QueryRequest):
#     try:
#         document_answer = get_response(request.question)
        
#         if document_answer and document_answer.strip():
#             return {"answer": document_answer}
#         else:
#             return {"answer": "No relevant documents found."}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_from_hf(request: QueryRequest, token: dict = Depends(verify_token)):
    try:
        response = query_huggingface(request.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint untuk query dari Hugging Face
# @app.post("/query")
# def query_from_hf(request: QueryRequest):
#     try:
#         response = query_huggingface(request.question)
#         return {"answer": response}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    try:
        # Pastikan folder data ada
        os.makedirs(DATA_FOLDER, exist_ok=True)

        file_path = os.path.join(DATA_FOLDER, file.filename)
        
        # Simpan file yang diunggah
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Tambahkan ke index
        add_document(file_path)
    
        return {"message": f"File {file.filename} berhasil diunggah dan diproses."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saat ingest file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)