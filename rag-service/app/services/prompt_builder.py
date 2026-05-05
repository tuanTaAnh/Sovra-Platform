from __future__ import annotations

from app.utils.prompt_loader import render_prompt


def format_chat_history(
    chat_history: list[dict] | None,
    max_chars: int = 3000,
) -> str:
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


def format_local_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No local context found."

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

    return "\n\n".join(context_parts)


def build_answer_prompt(
    question: str,
    chunks: list[dict],
    chat_history: list[dict] | None = None,
    standalone_question: str | None = None,
) -> str:
    history_text = format_chat_history(chat_history)
    local_context = format_local_context(chunks)

    standalone_question_line = ""

    if standalone_question and standalone_question.strip() != question.strip():
        standalone_question_line = (
            f"Rewritten standalone question: {standalone_question.strip()}"
        )

    return render_prompt(
        "rag_answer_prompt.txt",
        chat_history=history_text or "No previous conversation.",
        local_context=local_context,
        question=question,
        standalone_question_line=standalone_question_line,
    )


def build_rewrite_question_prompt(
    question: str,
    chat_history: list[dict] | None = None,
) -> str:
    history_text = format_chat_history(chat_history, max_chars=2500)

    return render_prompt(
        "rewrite_question_prompt.txt",
        chat_history=history_text or "No previous conversation.",
        question=question,
    )
