#!/bin/sh
set -eux

EMBEDDING_MODEL="${EMBEDDING_MODEL:-all-minilm}"
LLM_MODEL="${LLM_MODEL:-llama3.2:1b}"

echo "Waiting for Ollama..."
until curl -fsS http://ollama:11434/api/tags >/dev/null; do
  sleep 2
done

echo "Pulling embedding model: ${EMBEDDING_MODEL}"
curl -fsS http://ollama:11434/api/pull \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${EMBEDDING_MODEL}\"}"

echo "Pulling LLM model: ${LLM_MODEL}"
curl -fsS http://ollama:11434/api/pull \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${LLM_MODEL}\"}"

echo "Preloading embedding model: ${EMBEDDING_MODEL}"
curl -fsS http://ollama:11434/api/embed \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${EMBEDDING_MODEL}\",\"input\":\"warm up\",\"keep_alive\":-1}"

echo "Preloading LLM model: ${LLM_MODEL}"
curl -fsS http://ollama:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${LLM_MODEL}\",\"prompt\":\"Say OK only.\",\"stream\":false,\"keep_alive\":-1,\"options\":{\"num_predict\":5}}"

echo "Ollama models are ready and kept alive."