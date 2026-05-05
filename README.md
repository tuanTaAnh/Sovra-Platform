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
cp infra/env/.env.example infra/env/.env
```

```bash
Milvus:
docker compose --env-file infra/env/.env -f infra/docker/milvus.compose.yml up -d
```

```bash
Ollama:
docker compose --env-file infra/env/.env -f infra/docker/ollama.compose.yml up -d

curl http://localhost:11434/api/tags

curl http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"model":"all-minilm"}'

curl http://localhost:11434/api/pull \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3:8b"}'

curl http://localhost:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{"model":"all-minilm","input":"warm up","keep_alive":-1}'

curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3:8b","prompt":"Say OK only.","stream":false,"keep_alive":-1,"options":{"num_predict":5}}'

curl http://localhost:11434/api/ps
```

```bash
ingest-service:
cd ~/Sovra-Platform
conda create -n sovra-ingest python=3.11 -y
conda activate sovra-ingest
pip install -r ingest-service/requirements.txt

cd ingest-service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

curl -X POST http://localhost:8002/ingest/run -H "Content-Type: application/json" -d '{"reindex": true}'
```

```bash
rag-service:
cd ~/Sovra-Platform
conda create -n sovra-rag python=3.11 -y
conda activate sovra-rag
pip install -r rag-service/requirements.txt

cd rag-service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

curl -X POST http://localhost:8001/rag/query -H "Content-Type: application/json" -d '{"query":"What should I do if tire pressure is low?","top_k":3}'
```

```bash
Backend API:
cd ~/Sovra-Platform
conda create -n sovra-backend python=3.11 -y
conda activate sovra-backend

pip install -r backend-api/requirements.txt

cd backend-api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

