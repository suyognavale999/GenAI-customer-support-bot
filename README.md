# GenAI Customer Support Bot

A production-oriented customer support chatbot built using Python, FastAPI, SQLAlchemy, SQLite, ChromaDB and Retrieval-Augmented Generation (RAG).

The bot processes uploaded knowledge documents and generates context-based answers with source references. It includes JWT-based admin authentication, document management, guardrails, conversation storage, testing and a simple web interface.

## Features

- FastAPI REST API
- SQLite database with SQLAlchemy
- JWT-based admin authentication
- Knowledge document upload and management
- PDF, DOCX, TXT and Markdown text extraction
- Document chunking and embeddings
- Persistent ChromaDB vector storage
- Retrieval-Augmented Generation
- Provider-independent LLM integration
- Conversation and message history
- Source citations
- Prompt injection protection
- Topic-based guardrails
- User feedback support
- Structured logging
- Pytest test coverage
- Simple HTML, CSS and JavaScript chat interface
- Docker and Render deployment support

## Technology Stack

- Python 3.13
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- ChromaDB
- Pydantic
- JWT
- Pytest
- HTML, CSS and JavaScript
- Docker
- Render

## Project Structure

```text
genai-customer-support-bot/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── dependencies.py
│   │   └── router.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── rag/
│   ├── web/
│   │   ├── index.html
│   │   └── static/
│   │       ├── style.css
│   │       └── app.js
│   └── main.py
├── data/
│   ├── chroma/
│   ├── sqlite/
│   └── uploads/
├── logs/
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/suyognavale999/GenAI-customer-support-bot.git
cd genai-customer-support-bot
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file using `.env.example`:

```powershell
Copy-Item .env.example .env
```

### 5. Start the application

```powershell
uvicorn app.main:app --reload --reload-exclude ".venv/*"
```

Application:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/api/v1/health
```

## Admin Authentication

1. Open Swagger at `http://127.0.0.1:8000/docs`.
2. Execute `POST /api/v1/auth/login`.
3. Enter the configured admin username and password.
4. Copy the returned access token.
5. Click **Authorize** in Swagger.
6. Paste the token and authorize.
7. Test the protected admin APIs.

## Knowledge Base Workflow

1. Admin logs in.
2. Admin uploads a supported document.
3. The application validates the file.
4. Text is extracted and cleaned.
5. The document is split into chunks.
6. Embeddings are generated.
7. Chunks are stored in ChromaDB.
8. The chatbot retrieves relevant chunks.
9. The LLM generates a context-based answer.
10. The response includes source information.

## Running Tests

```powershell
python -m pytest -v
```

Current tests include:

- Health endpoint
- Valid support questions
- Unrelated-question blocking
- Prompt-injection blocking

## Security

The application includes:

- Password hashing
- JWT authentication
- Protected admin routes
- File type and size validation
- Prompt injection checks
- Topic restrictions
- Environment-based secrets
- Safe fallback responses
- Sensitive-value masking
- Request validation

## Future Improvements

- PostgreSQL database support
- Managed vector database integration
- Azure AI Search support
- Azure OpenAI integration
- Streaming chat responses
- Advanced RAG evaluation
- Hybrid retrieval
- Reranking
- Admin dashboard
- Role-based access control
- CI/CD pipeline
- Production monitoring

## Disclaimer

This project is built for learning, demonstration and portfolio purposes. Do not upload confidential, private or production data without completing an appropriate security review.

## Author

**Suyog Navale**

Python Backend and GenAI Developer