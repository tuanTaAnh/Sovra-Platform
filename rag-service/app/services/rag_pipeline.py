from __future__ import annotations

from time import perf_counter

from app.clients.ollama_client import OllamaClient
from app.clients.milvus_store import MilvusStore
from app.core.config import settings
from app.services.prompt_builder import build_prompt, format_chat_history


def elapsed_ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 2)


class RagPipeline:
    def __init__(self) -> None:
        self.ollama = OllamaClient(settings.ollama_base_url)
        self.store = MilvusStore(
            settings.milvus_host,
            settings.milvus_port,
            settings.milvus_collection,
        )

    def rewrite_question(
        self,
        question: str,
        chat_history: list[dict] | None = None,
    ) -> str:
        if not chat_history:
            return question

        history_text = format_chat_history(chat_history, max_chars=2500)

        rewrite_prompt = f"""
Rewrite the current user question into a standalone search question.

Rules:
- Use the conversation history to resolve references like "it", "that one", "the first one", "the second option", "those 3 types".
- Keep the rewritten question short.
- Do not answer the question.
- Do not add facts that are not in the conversation.
- Return only the rewritten standalone question.

Conversation history:
{history_text}

Current user question:
{question}

Standalone question:
""".strip()

        rewritten = self.ollama.generate(settings.llm_model, rewrite_prompt).strip()

        if not rewritten:
            return question

        return rewritten

    def query(
        self,
        question: str,
        top_k: int | None = None,
        chat_history: list[dict] | None = None,
    ) -> dict:
        total_start = perf_counter()
        timings: dict = {}

        top_k = top_k or settings.default_top_k
        chat_history = chat_history or []

        rewrite_start = perf_counter()
        standalone_question = self.rewrite_question(
            question=question,
            chat_history=chat_history,
        )
        timings["question_rewrite_ms"] = elapsed_ms(rewrite_start)

        embedding_start = perf_counter()
        query_vector = self.ollama.embed(
            settings.embedding_model,
            standalone_question,
        )
        timings["query_embedding_ms"] = elapsed_ms(embedding_start)

        milvus_start = perf_counter()
        chunks, milvus_timings = self.store.search_with_timing(
            query_vector=query_vector,
            top_k=top_k,
        )
        timings["milvus"] = milvus_timings
        timings["milvus_total_wrapper_ms"] = elapsed_ms(milvus_start)

        prompt_start = perf_counter()
        prompt = build_prompt(
            question=question,
            chunks=chunks,
            chat_history=chat_history,
            standalone_question=standalone_question,
        )
        timings["prompt_build_ms"] = elapsed_ms(prompt_start)

        llm_start = perf_counter()
        answer = self.ollama.generate(settings.llm_model, prompt)
        timings["llm_generate_ms"] = elapsed_ms(llm_start)

        format_start = perf_counter()
        response = {
            "answer": answer,
            "sources": [
                {
                    "source": c.get("source"),
                    "doc_type": c.get("doc_type"),
                    "score": c.get("score"),
                    "preview": (c.get("text") or "")[:240],
                }
                for c in chunks
            ],
            "retrieval_used": bool(chunks),
            "llm_model": settings.llm_model,
            "embedding_model": settings.embedding_model,
            "collection": settings.milvus_collection,
            "mode": "local",
            "cloud_api_required": False,
            "standalone_question": standalone_question,
        }
        timings["response_format_ms"] = elapsed_ms(format_start)
        timings["total_ms"] = elapsed_ms(total_start)

        response["timings_ms"] = timings

        return response
