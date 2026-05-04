from __future__ import annotations


def build_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    context_blocks = []
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        context_blocks.append(
            f"[Source {idx}]\n"
            f"Document: {chunk.get('source')}\n"
            f"Type: {chunk.get('doc_type')}\n"
            f"Content:\n{chunk.get('text')}"
        )

    context = "\n\n".join(context_blocks) if context_blocks else "No relevant local context was found."

    return f"""
        You are Sovra AI, a private embedded AI assistant for automotive and enterprise use cases.
        Answer using only the local context below when possible.
        If the context is insufficient, say that the local knowledge base does not contain enough information.
        Keep the answer clear, practical, and safety-aware.
        
        LOCAL CONTEXT:
        {context}
        
        USER QUESTION:
        {question}
        
        ANSWER:
    """.strip()