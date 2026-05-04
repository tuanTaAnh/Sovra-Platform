from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def load_documents(docs_path: str) -> list[dict]:
    root = Path(docs_path)
    if not root.exists():
        raise FileNotFoundError(f"Docs path does not exist: {docs_path}")

    docs: list[dict] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            text = path.read_text(encoding="utf-8")
            doc_type = path.parent.name if path.parent != root else "general"
            docs.append(
                {
                    "source": str(path.relative_to(root)),
                    "doc_type": doc_type,
                    "text": text,
                }
            )
    return docs
