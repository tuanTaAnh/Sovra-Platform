from __future__ import annotations

import requests


class OllamaClient:
    def __init__(self, base_url: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.ok
        except requests.RequestException:
            return False

    def embed(self, model: str, text: str) -> list[float]:
        response = requests.post(
            f"{self.base_url}/api/embed",
            json={
                "model": model,
                "input": text,
                "keep_alive": -1,
            },
            timeout=self.timeout,
        )

        if not response.ok:
            raise RuntimeError(
                f"Ollama embed failed. "
                f"Status={response.status_code}. "
                f"Response={response.text}"
            )

        payload = response.json()
        embeddings = payload.get("embeddings")

        if not embeddings:
            raise RuntimeError(f"Ollama returned no embeddings: {payload}")

        return embeddings[0]