#!/usr/bin/env bash
set -e

export APP_VERSION="${APP_VERSION:-hf-demo}"
export ENVIRONMENT="${ENVIRONMENT:-huggingface}"

export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"

export LLM_MODEL="${LLM_MODEL:-llama3.2:1b}"
export EMBEDDING_MODEL="${EMBEDDING_MODEL:-all-minilm}"

export MILVUS_DB_PATH="${MILVUS_DB_PATH:-/app/milvus/sovra_milvus.db}"
export MILVUS_COLLECTION="${MILVUS_COLLECTION:-sovra_knowledge_base}"

export DOCS_PATH="${DOCS_PATH:-/app/data/docs}"
export CHUNK_SIZE="${CHUNK_SIZE:-900}"
export CHUNK_OVERLAP="${CHUNK_OVERLAP:-150}"

export DEFAULT_TOP_K="${DEFAULT_TOP_K:-3}"

export RAG_SERVICE_URL="${RAG_SERVICE_URL:-http://127.0.0.1:8001}"
export INGEST_SERVICE_URL="${INGEST_SERVICE_URL:-http://127.0.0.1:8002}"
export DATABASE_URL="${DATABASE_URL:-sqlite:////app/data/backend_api.db}"
export HTTP_TIMEOUT_SECONDS="${HTTP_TIMEOUT_SECONDS:-600}"

export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:5173,http://localhost:3000,http://localhost:8080,http://localhost}"

mkdir -p /app/data
mkdir -p /app/milvus

echo "Starting Ollama..."
ollama serve &

echo "Waiting for Ollama..."
until curl -fsS "${OLLAMA_BASE_URL}/api/tags" >/dev/null; do
  sleep 2
done

if [ "${SKIP_MODEL_PULL:-false}" != "true" ]; then
  echo "Pulling embedding model: ${EMBEDDING_MODEL}"
  ollama pull "${EMBEDDING_MODEL}"

  echo "Pulling LLM model: ${LLM_MODEL}"
  ollama pull "${LLM_MODEL}"
else
  echo "Skipping model pull because SKIP_MODEL_PULL=true"
fi

echo "Preloading embedding model..."
curl -fsS "${OLLAMA_BASE_URL}/api/embed" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${EMBEDDING_MODEL}\",\"input\":\"warm up\",\"keep_alive\":-1}" >/dev/null

echo "Preloading LLM model..."
curl -fsS "${OLLAMA_BASE_URL}/api/generate" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${LLM_MODEL}\",\"prompt\":\"Say OK only.\",\"stream\":false,\"keep_alive\":-1,\"options\":{\"num_predict\":5}}" >/dev/null

echo "Starting ingest-service..."
cd /app/ingest-service
uvicorn app.main:app --host 127.0.0.1 --port 8002 &

echo "Waiting for ingest-service..."
until curl -fsS http://127.0.0.1:8002/health >/dev/null; do
  sleep 2
done

echo "Reindexing documents into Milvus Lite..."
curl -fsS -X POST http://127.0.0.1:8002/ingest/run \
  -H "Content-Type: application/json" \
  -d '{"reindex": true}'

echo "Starting rag-service..."
cd /app/rag-service
uvicorn app.main:app --host 127.0.0.1 --port 8001 &

echo "Waiting for rag-service..."
until curl -fsS http://127.0.0.1:8001/health >/dev/null; do
  sleep 2
done

echo "Starting backend-api on port 7860..."
cd /app/backend-api
exec uvicorn app.main:app --host 0.0.0.0 --port 7860