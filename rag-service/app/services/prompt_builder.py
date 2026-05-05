from __future__ import annotations


def format_chat_history(chat_history: list[dict] | None, max_chars: int = 3000) -> str:
    if not chat_history:
        return ""

    lines = []

    for item in chat_history:
        role = item.get("role", "user")
        content = (item.get("content") or "").strip()

        if not content:
            continue

        if role == "assistant":
            lines.append(f"Assistant: {content}")
        else:
            lines.append(f"User: {content}")

    text = "\n".join(lines)

    if len(text) > max_chars:
        text = text[-max_chars:]

    return text


def build_prompt(
    question: str,
    chunks: list[dict],
    chat_history: list[dict] | None = None,
    standalone_question: str | None = None,
) -> str:
    history_text = format_chat_history(chat_history)

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        source = chunk.get("source", "unknown")
        doc_type = chunk.get("doc_type", "unknown")
        text = chunk.get("text", "")

        context_parts.append(
            f"[Source {index}]\n"
            f"source: {source}\n"
            f"doc_type: {doc_type}\n"
            f"content:\n{text}"
        )

    context_text = "\n\n".join(context_parts) if context_parts else "No local context found."

    standalone_line = ""
    if standalone_question and standalone_question.strip() != question.strip():
        standalone_line = f"\nRewritten standalone question: {standalone_question}\n"

    return f"""
        You are Sovra AI, a local RAG assistant.

        Use the local context first.
        If the local context does not contain the answer, say that the local context does not provide enough information.
        Do not invent facts, prices, sales numbers, or vehicle counts.

        Conversation history:
        {history_text if history_text else "No previous conversation."}

        Local context:
        {context_text}

        Current user question:
        {question}
        {standalone_line}

        Answer clearly and concisely.
    """.strip()