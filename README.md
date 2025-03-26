# FastAPI with Hugging Face & Supabase Integration

This is a FastAPI application that integrates with Hugging Face for natural language processing, Supabase for authentication, and a file ingestion feature. It also uses JWT for authentication, and supports CORS for front-end applications.

## Features

- **User Authentication**: Sign up and login with email and password using Supabase authentication.
- **Query Hugging Face Model**: Send a query to the Hugging Face API (Mistral-7B-Instruct) and get a response.
- **File Ingestion**: Upload and ingest files to process and store them on the server.
- **JWT Authentication**: Use JWT tokens for authenticating API requests.


## Setup

### Prerequisites

- Python 3.7 or higher
- `pip` for managing dependencies

### Environment Variables

Make sure to create a `.env` file in the root directory of your project with the following variables:

```env
HUGGINGFACEHUB_API_TOKEN=<Your Hugging Face API Token>
SUPABASE_JWT_SECRET=<Your Supabase JWT Secret>
PORT=8000  # Optional, default to 8000


# INSTALATION
1. Clone this repository:

```git clone https://github.com/alvianainh/chatbot-rag.git```

2. Create a virtual environment and install dependencies:

```venv\Scripts\activate```
```pip install -r requirements.txt```

3. Create the .env file (as described above) to store your secrets.

#RUNNING THE APPLICATION
To start the FastAPI app, use Uvicorn:

```uvicorn main:app --reload```
The application will run on http://127.0.0.1:8000.

# API ENDPOINTS

1. POST /register
Registers a new user with an email and password.
Request Body:

{
  "email": "user@example.com",
  "password": "yourpassword"
}

Response
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}

2. POST /token

Logs in and returns a JWT token.
Request Body:
{
  "email": "user@example.com",
  "password": "yourpassword"
}

Response

{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}

3. POST /query
Queries the Hugging Face model with a question. Requires a Bearer token for authentication.

Request Body:
{
  "question": "What is the capital of France?"
}

Authorization Header:

Authorization: Bearer <JWT_TOKEN>

Response:

{
  "user": "user@example.com",
  "question": "What is the capital of France?",
  "answer": "The capital of France is Paris."
}


4. POST /ingest
Uploads a file for ingestion and processing.
Request Body: Multipart file upload.
Response:

{
  "message": "File <filename> successfully uploaded and processed."
}


## Running the Application
Run the frontend application with the following command

 ```npm run start```

 The application will run at http://localhost:3000 by default.

 ## Using the Application

 Registration/Login
Users must first register through the registration page.

After registering, users can log in to obtain an access token.

Using the AI Chatbot
After logging in, users can ask questions to the chatbot.


