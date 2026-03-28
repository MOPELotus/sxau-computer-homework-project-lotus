from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import requests


class SiliconFlowAPIError(RuntimeError):
    """Raised when SiliconFlow returns an invalid response."""


def _extract_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise SiliconFlowAPIError("Model response did not contain a valid JSON object.")


@dataclass
class SiliconFlowClient:
    api_key: str
    base_url: str
    chat_model: str
    embedding_model: str
    timeout: int = 60
    session: requests.Session = field(default_factory=requests.Session)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}{endpoint}",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        if not response.ok:
            raise SiliconFlowAPIError(
                f"SiliconFlow request failed ({response.status_code}): {response.text[:300]}"
            )
        return response.json()

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1024,
            "enable_thinking": False,
        }
        response = self._post("/chat/completions", payload)
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise SiliconFlowAPIError("SiliconFlow chat response schema changed.") from exc

        return _extract_json_object(content), response

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        payload = {
            "model": self.embedding_model,
            "input": texts,
            "encoding_format": "float",
        }
        response = self._post("/embeddings", payload)
        try:
            return [item["embedding"] for item in response["data"]]
        except KeyError as exc:
            raise SiliconFlowAPIError("SiliconFlow embedding response schema changed.") from exc

    def list_models(self, sub_type: str | None = None) -> list[dict[str, Any]]:
        params = {}
        if sub_type:
            params["sub_type"] = sub_type
        response = self.session.get(
            f"{self.base_url}/models",
            headers={"Authorization": f"Bearer {self.api_key}"},
            params=params,
            timeout=self.timeout,
        )
        if not response.ok:
            raise SiliconFlowAPIError(
                f"Failed to list models ({response.status_code}): {response.text[:300]}"
            )
        data = response.json()
        return data.get("data", [])
