COMPOSE=docker compose -f infra/docker/compose.yml

up:
	$(COMPOSE) up --build

up-detached:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ingest:
	curl -X POST http://localhost:8002/ingest/run -H 'Content-Type: application/json' -d '{"reindex": true}'

query:
	curl -X POST http://localhost:8001/rag/query -H 'Content-Type: application/json' -d '{"query":"What should I do if tire pressure is low?","top_k":3}'