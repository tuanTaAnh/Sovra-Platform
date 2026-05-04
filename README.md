# Sovra AI Platform Starter

This starter contains a local RAG stack for Sovra AI:

- Milvus vector database
- Ollama model runtime
- `bge-m3` embedding model
- `llama3` answer generation model
- FastAPI RAG query service
- FastAPI ingest service
- Dummy automotive and enterprise documents

## Run

```bash
Milvus:
docker compose --env-file infra/env/.env -f infra/docker/milvus.compose.yml up -d
```

```bash
Ollama:
docker compose --env-file infra/env/.env -f infra/docker/ollama.compose.yml up -d

curl http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"model":"bge-m3"}'
  
curl http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3"}'
```

```bash
ingest-service:
conda create -n sovra-ingest python=3.11 -y
conda activate sovra-ingest
pip install -r ingest-service/requirements.txt

export OLLAMA_BASE_URL=http://localhost:11434
export EMBEDDING_MODEL=bge-m3

export MILVUS_HOST=localhost
export MILVUS_PORT=19530
export MILVUS_COLLECTION=sovra_knowledge_base

export DOCS_PATH="$PWD/data/docs"
export CHUNK_SIZE=900
export CHUNK_OVERLAP=150

cd ingest-service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

curl -X POST http://localhost:8002/ingest/run -H "Content-Type: application/json" -d '{"reindex": true}'
```

```bash
rag-service:
cd sovra-platform
conda create -n sovra-rag python=3.11 -y
conda activate sovra-rag
pip install -r rag-service/requirements.txt

export OLLAMA_BASE_URL=http://localhost:11434
export LLM_MODEL=llama3
export EMBEDDING_MODEL=bge-m3

export MILVUS_HOST=localhost
export MILVUS_PORT=19530
export MILVUS_COLLECTION=sovra_knowledge_base

export DEFAULT_TOP_K=4

cd rag-service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

curl -X POST http://localhost:8001/rag/query -H "Content-Type: application/json" -d '{"query":"What should I do if tire pressure is low?","top_k":3}'
```
