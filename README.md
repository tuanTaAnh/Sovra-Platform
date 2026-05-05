# Sovra AI Platform

**Sovra AI**  
**Sovereign Intelligence. Private by Design.**

Sovra AI is a private / embedded AI platform designed to run locally or on-premise, with a focus on automotive and enterprise use cases.

This repository contains the backend platform for Sovra AI.

Frontend repository:  
https://github.com/tuanTaAnh/Sovra-Frontend

---

## 1. Overview

Sovra AI demonstrates a local AI assistant that can run on a single VM without depending on external cloud AI APIs.

The platform combines FastAPI backend services, local LLM inference, local embedding generation, Retrieval-Augmented Generation, Milvus vector search, and a local document knowledge base.

The MVP is designed to show how private AI can support automotive and enterprise workflows while keeping data inside a local or on-premise environment.

---

## 2. System Capabilities

Sovra AI Platform currently supports:

- Local AI inference with Ollama
- Local embedding generation
- Local document ingestion
- Vector search over indexed documents
- RAG-based question answering
- Automotive knowledge assistant
- Enterprise document Q&A
- Conversation history through the backend API
- Knowledge base reindexing
- Single-VM Docker deployment

The demo highlights:

- Running locally
- No cloud AI API required
- Private by design
- Automotive knowledge enabled

---

## 3. Main Use Cases

### Vehicle Manual Assistant

Users can ask vehicle-related questions and receive answers from local vehicle manual documents.

Example questions:

```text
How do I enable lane assist?
How do I connect my phone to the vehicle?
What should I check if Lane Assist is unavailable?
```

### Troubleshooting Assistant

Users can ask about vehicle warnings and receive safe next-step guidance.

Example questions:

```text
What should I do if tire pressure is low?
What should I do when the battery warning light appears?
The charging port does not open. What should I try?
```

### EV Charging Guidance

Users can ask about EV efficiency, charging behavior, and fast charging.

Example questions:

```text
How can I improve EV battery efficiency?
Should I charge my EV to 100 percent every day?
Is fast charging okay for long trips?
```

### Driver Support Assistant

The assistant can provide short, safety-aware support answers for in-car assistant scenarios.

Example questions:

```text
Can Lane Assist drive for me?
What does the tire pressure warning mean?
Can the assistant answer voice questions?
```

### Private Enterprise Assistant

The same architecture can be adapted to internal company documents.

Example questions:

```text
How can Sovra AI be used for private document Q&A?
How does on-premise deployment reduce data leakage risk?
How should the assistant handle restricted documents?
```

---

## 4. Architecture

```text
Frontend Website
    ↓
Backend API
    ↓
RAG Service
    ↓
Ollama + Milvus
    ↓
Local Knowledge Base
```

Main services:

```text
backend-api
    Public API layer used by the frontend.

rag-service
    Handles RAG query flow: embedding, vector search, prompt building, and LLM generation.

ingest-service
    Reads local documents, chunks them, generates embeddings, and stores vectors in Milvus.

ollama
    Runs the local LLM and embedding model.

milvus
    Stores and searches document embeddings.

etcd + minio
    Required by Milvus standalone mode.
```

---

## 5. Project Structure

```text
Sovra-Platform/
├── backend-api/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
│
├── rag-service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
│
├── ingest-service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   └── docs/
│       ├── automotive/
│       └── enterprise/
│
├── infra/
│   ├── docker/
│   │   ├── milvus.compose.yml
│   │   ├── ollama.compose.yml
│   │   ├── ingest-service.compose.yml
│   │   ├── rag-service.compose.yml
│   │   └── backend-api.compose.yml
│   │
│   └── env/
│       └── .env.docker
│
└── README.md
```

---

## 6. Related Repository

The frontend is maintained in a separate repository:

```text
https://github.com/tuanTaAnh/Sovra-Frontend
```

---

## 7. Docker Deployment

This section assumes Docker and Docker Compose are already installed.

### 7.1 Clone Repository

```bash
git clone https://github.com/tuanTaAnh/Sovra-Platform.git
cd Sovra-Platform
```

### 7.2 Create Shared Docker Network

```bash
docker network create sovra-net
```

If the network already exists, this command can be ignored.

All services use the same external Docker network so they can communicate by service name.

### 7.3 Configure Environment

Create or verify:

```text
infra/env/.env.docker
```

Example:

```env
APP_VERSION=docker
ENVIRONMENT=docker

# Backend API
BACKEND_API_PORT=8000
RAG_SERVICE_URL=http://rag-service:8001
INGEST_SERVICE_URL=http://ingest-service:8002
CORS_ORIGINS=http://localhost,http://127.0.0.1,http://localhost:80,http://127.0.0.1:80
DATABASE_URL=sqlite:////app/data/backend_api.db
HTTP_TIMEOUT_SECONDS=240

# RAG Service
RAG_SERVICE_PORT=8001
DEFAULT_TOP_K=4

# Ingest Service
INGEST_SERVICE_PORT=8002
DOCS_PATH=/app/data/docs
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Ollama
OLLAMA_PORT=11434
OLLAMA_BASE_URL=http://ollama:11434
LLM_MODEL=llama3:8b
EMBEDDING_MODEL=all-minilm

# Milvus
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_UI_PORT=9091
MILVUS_COLLECTION=sovra_knowledge_base

# MinIO for Milvus standalone
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

---

## 8. Start Backend Platform

Run these commands from the `Sovra-Platform` root.

### Start Milvus

```bash
docker compose \
  -f infra/docker/milvus.compose.yml \
  up -d
```

### Start Ollama

```bash
docker compose \
  -f infra/docker/ollama.compose.yml \
  up -d ollama
```

### Pull and Preload Models

```bash
docker compose \
  -f infra/docker/ollama.compose.yml \
  up ollama-init
```

### Start Ingest Service

```bash
docker compose \
  -f infra/docker/ingest-service.compose.yml \
  up -d --build
```

### Start RAG Service

```bash
docker compose \
  -f infra/docker/rag-service.compose.yml \
  up -d --build
```

### Start Backend API

```bash
docker compose \
  -f infra/docker/backend-api.compose.yml \
  up -d --build
```

---

### 9.1 Trigger Ingestion After Updating Files

To update the knowledge base, add or modify document files under:

```text
data/docs/
```

Example structure:

```text
data/docs/
├── automotive/
│   ├── vehicle_manual.md
│   ├── troubleshooting_faq.md
│   └── ev_charging_guide.md
│
└── enterprise/
    └── enterprise_policy_sample.md
```

After adding, editing, or deleting files, trigger the ingest service again:

```bash
curl -X POST http://localhost:8002/ingest/run \
  -H "Content-Type: application/json" \
  -d '{"reindex": true}'
```

This command rebuilds the vector index from the current files in `data/docs/`.

In Docker deployment, the `data/docs` folder is mounted into the ingest container, so the container can read the updated files from the host machine. Docker bind mounts allow a file or directory on the host machine to be mounted into a container. 

After reindexing, test the updated knowledge base:

```bash
curl -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What should I do if tire pressure is low?","top_k":3,"chat_history":[]}'
```

---

## 10. Test Backend

Test RAG service:

```bash
curl -X POST http://localhost:8001/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What should I do if tire pressure is low?","top_k":3,"chat_history":[]}'
```

Test Backend API:

```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I enable lane assist?","top_k":3,"save_history":true}'
```

Expected result:

```text
HTTP 200 OK
answer
sources
retrieval_used=true
llm_model
embedding_model
timings_ms
```

---

## 11. Stop Services

```bash
docker compose -f infra/docker/backend-api.compose.yml down
docker compose -f infra/docker/rag-service.compose.yml down
docker compose -f infra/docker/ingest-service.compose.yml down
docker compose -f infra/docker/ollama.compose.yml down
docker compose -f infra/docker/milvus.compose.yml down
```

Do not add `-v` unless you intentionally want to remove persistent volumes.

---

## 12. Notes

This is an MVP / concept system. It is designed to demonstrate a working private AI assistant architecture, not a production-hardened deployment.

Potential improvements:

- Authentication and user management
- Role-based document access control
- Streaming responses
- Larger automotive knowledge base
- Voice interface integration
- Better admin UI for knowledge base management
- Production-grade secrets management