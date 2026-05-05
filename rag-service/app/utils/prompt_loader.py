from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any


APP_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = APP_DIR / "prompts"


@lru_cache(maxsize=32)
def load_prompt_template(prompt_name: str) -> str:
    """
    Load a prompt template from app/prompts.

    Example:
        load_prompt_template("rag_answer_prompt.txt")
    """
    prompt_path = PROMPTS_DIR / prompt_name

    if not prompt_path.exists():
        available_prompts = sorted(
            path.name for path in PROMPTS_DIR.glob("*.txt")
        )

        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}. "
            f"Available prompts: {available_prompts}"
        )

    return prompt_path.read_text(encoding="utf-8")


def render_prompt(prompt_name: str, **values: Any) -> str:
    """
    Render a prompt file using string.Template.

    Placeholders in prompt files should use:
        ${placeholder_name}
    """
    template_text = load_prompt_template(prompt_name)

    safe_values = {
        key: "" if value is None else str(value)
        for key, value in values.items()
    }

    return Template(template_text).safe_substitute(safe_values).strip()


def clear_prompt_cache() -> None:
    """
    Optional helper for development if you want to reload prompt files
    without restarting the process.
    """
    load_prompt_template.cache_clear()
