FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV APP_VERSION=hf-demo
ENV ENVIRONMENT=huggingface

ENV OLLAMA_HOST=127.0.0.1:11434
ENV OLLAMA_BASE_URL=http://127.0.0.1:11434

ENV LLM_MODEL=llama3.2:1b
ENV EMBEDDING_MODEL=all-minilm

ENV MILVUS_DB_PATH=/app/milvus/sovra_milvus.db
ENV MILVUS_COLLECTION=sovra_knowledge_base

ENV DOCS_PATH=/app/data/docs
ENV CHUNK_SIZE=900
ENV CHUNK_OVERLAP=150
ENV DEFAULT_TOP_K=3

ENV RAG_SERVICE_URL=http://127.0.0.1:8001
ENV INGEST_SERVICE_URL=http://127.0.0.1:8002
ENV DATABASE_URL=sqlite:////app/data/backend_api.db
ENV HTTP_TIMEOUT_SECONDS=600

ENV CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080,http://localhost

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    build-essential \
    procps \
    zstd \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

COPY backend-api ./backend-api
COPY rag-service ./rag-service
COPY ingest-service ./ingest-service
COPY data ./data
COPY start-backend.sh ./start-backend.sh

RUN chmod +x ./start-backend.sh

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend-api/requirements.txt \
    && pip install --no-cache-dir -r rag-service/requirements.txt \
    && pip install --no-cache-dir -r ingest-service/requirements.txt

EXPOSE 7860

CMD ["./start-backend.sh"]