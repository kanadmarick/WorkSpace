"""Task-aware local Ollama router for installation as an Open WebUI Pipe."""

import asyncio
import json
import logging
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

LOGGER = logging.getLogger("open_webui.model_router")
VALID_CATEGORIES = frozenset({"code", "chat", "math", "writing"})
FALLBACK_CATEGORY = "chat"
MODEL_INFO_PATH = Path(__file__).with_name("MODEL_INFO.md")
CLASSIFIER_PROMPT = (
    "Classify the user's latest message into exactly one label: code, chat, math, or writing. "
    "Return only that one lowercase label. "
    "Use code for programming, debugging, APIs, or technical implementation. "
    "Use math for calculations, formal logic, or mathematical proofs. "
    "Use writing for drafting, rewriting, editing, or creative prose. "
    "Use chat for everything else."
)


def _default_model_info() -> dict[str, dict[str, str]]:
    return {
        "code": {"easy": "qwen2.5:3b", "default": "qwen2.5-coder:7b"},
        "chat": {"easy": "llama3.2:3b", "default": "qwen3:8b"},
        "math": {"easy": "qwen2.5:3b", "default": "deepseek-r1:7b"},
        "writing": {"easy": "llama3.2:3b", "default": "mistral:7b"},
    }


def _read_model_info() -> dict[str, dict[str, str]]:
    if not MODEL_INFO_PATH.exists():
        return _default_model_info()

    text = MODEL_INFO_PATH.read_text(encoding="utf-8")
    start = text.find("<!-- model-routing-config:start -->")
    end = text.find("<!-- model-routing-config:end -->")
    if start == -1 or end == -1 or end <= start:
        return _default_model_info()
    payload = text[start + len("<!-- model-routing-config:start -->") : end].strip()
    parsed = json.loads(payload)
    return {str(key): {str(k): str(v) for k, v in value.items()} for key, value in parsed.items()}


MODEL_ROUTING_INFO = _read_model_info()


def classify_question(question: str) -> str:
    if not question or not question.strip():
        return "chat"

    normalized = question.lower()
    if any(marker in normalized for marker in ("python", "javascript", "typescript", "function", "class ", "exception", "traceback", "error", "debug", "api", "sql", "code", "bug", "fix this", "deploy", "flask", "django", "react")):
        return "code"
    if any(marker in normalized for marker in ("calculate", "solve", "equation", "proof", "integral", "derivative", "statistics", "algebra", "+", "-", "*", "/")):
        return "math"
    if any(marker in normalized for marker in ("rewrite", "edit", "essay", "paragraph", "draft", "story", "poem", "email", "letter", "marketing copy", "blog")):
        return "writing"
    return "chat"


def is_simple_question(question: str) -> bool:
    if not question or not question.strip():
        return True
    text = question.strip()
    words = re.findall(r"\b[\w']+\b", text)
    if len(words) <= 12 and not any(marker in text.lower() for marker in ("compare", "design", "architecture", "debug", "explain step by step", "write a full", "proof", "analyze")):
        return True
    return False


def route_question(question: str) -> dict[str, str]:
    category = classify_question(question)
    routing = MODEL_ROUTING_INFO.get(category, MODEL_ROUTING_INFO["chat"])
    complexity = "easy" if is_simple_question(question) else "default"
    model = routing.get(complexity, routing.get("default", routing.get("easy", "qwen3:8b")))
    return {"category": category, "complexity": complexity, "model": model}


@dataclass
class SessionState:
    current_category: str
    current_model: str


class Pipe:
    class Valves(BaseModel):
        OLLAMA_BASE_URL: str = Field(
            default="http://127.0.0.1:11434",
            description="Base URL for the local Ollama API.",
        )
        CLASSIFIER_MODEL: str = Field(
            default="qwen2.5:1.5b",
            description="Small model used only to classify the latest user message.",
        )
        CATEGORY_MODELS_JSON: str = Field(
            default='{"code":"qwen2.5-coder:7b","chat":"qwen3:8b",'
            '"math":"deepseek-r1:7b","writing":"mistral:7b"}',
            description="JSON mapping of code, chat, math, and writing to Ollama model names.",
        )
        TASK_KEEP_ALIVE: str = Field(
            default="10m",
            description="How long the active task model stays loaded after a response.",
        )
        CLASSIFIER_NUM_GPU: int = Field(
            default=0,
            description="GPU layers for the classifier. Keep 0 to reserve VRAM for task models.",
        )
        TASK_NUM_GPU: int = Field(
            default=-1,
            description="GPU layers for task models. -1 asks Ollama to offload as much as possible.",
        )
        TEMPERATURE: float = Field(default=0.2, ge=0, le=2)

    def __init__(self) -> None:
        self.valves = self.Valves()
        self._sessions: dict[str, SessionState] = {}
        self._state_lock = asyncio.Lock()

    def pipes(self) -> list[dict[str, str]]:
        return [{"id": "smart-router", "name": "Smart Local Router"}]

    async def pipe(
        self, body: dict[str, Any], __user__: dict[str, Any] | None = None
    ) -> str | AsyncIterator[str]:
        messages = self._messages(body)
        if not messages:
            return "No chat messages were supplied."

        try:
            category_models = self._category_models()
        except ValueError as error:
            return f"Router configuration error: {error}"

        latest_text = self._latest_user_text(messages)
        category = await self._classify(latest_text)
        route = route_question(latest_text)
        model = route["model"]
        if model not in set(category_models.values()) and category in category_models:
            model = category_models[category]
        model = await self._select_task_model(category, category_models, model)
        session_key = self._session_key(body, __user__)

        async with self._state_lock:
            previous = self._sessions.get(session_key)
            swapped = previous is not None and previous.current_model != model
            self._sessions[session_key] = SessionState(category, model)

        LOGGER.info(
            "model_router category=%s model=%s swapped=%s session=%s",
            category,
            model,
            swapped,
            session_key,
        )

        if swapped and previous is not None:
            await self._unload(previous.current_model)

        payload = {
            "model": model,
            "messages": messages,
            "stream": body.get("stream", True),
            "keep_alive": self.valves.TASK_KEEP_ALIVE,
            "options": {
                "num_gpu": self.valves.TASK_NUM_GPU,
                "temperature": self.valves.TEMPERATURE,
            },
        }

        if body.get("stream", True):
            return self._stream_chat(payload)
        return await self._chat(payload)

    def _category_models(self) -> dict[str, str]:
        try:
            configured = json.loads(self.valves.CATEGORY_MODELS_JSON)
        except json.JSONDecodeError as error:
            raise ValueError("CATEGORY_MODELS_JSON must be valid JSON.") from error

        if not isinstance(configured, dict):
            raise ValueError("CATEGORY_MODELS_JSON must be a JSON object.")

        models = {str(key).lower(): str(value).strip() for key, value in configured.items()}
        missing = VALID_CATEGORIES.difference(models)
        empty = [category for category in VALID_CATEGORIES if not models.get(category)]
        if missing or empty:
            raise ValueError("Mappings for code, chat, math, and writing are required.")
        return models

    async def _select_task_model(self, category: str, category_models: dict[str, str], preferred: str | None = None) -> str:
        task_model = preferred or category_models.get(category)
        fallback = category_models.get(FALLBACK_CATEGORY, "")
        if not task_model:
            return fallback

        try:
            await self._probe_model(task_model)
            return task_model
        except (httpx.HTTPError, ValueError, TypeError):
            if not fallback:
                return task_model
            LOGGER.warning(
                "model_router model_unavailable category=%s model=%s fallback=%s",
                category,
                task_model,
                fallback,
            )
            return fallback

    async def _probe_model(self, model: str) -> None:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "stream": False,
            "keep_alive": 0,
            "options": {"num_gpu": self.valves.TASK_NUM_GPU, "temperature": 0},
        }
        await self._chat(payload)

    async def _classify(self, latest_text: str) -> str:
        if not latest_text:
            return "chat"

        normalized = latest_text.lower()
        if any(
            marker in normalized
            for marker in (
                "python",
                "javascript",
                "typescript",
                "function",
                "class ",
                "exception",
                "traceback",
                "error",
                "debug",
                "api",
                "sql",
                "code",
            )
        ):
            return "code"
        if any(
            marker in normalized
            for marker in ("calculate", "solve", "equation", "proof", "integral", "derivative")
        ):
            return "math"

        payload = {
            "model": self.valves.CLASSIFIER_MODEL,
            "messages": [
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user", "content": latest_text},
            ],
            "stream": False,
            "keep_alive": 0,
            "options": {"num_gpu": self.valves.CLASSIFIER_NUM_GPU, "temperature": 0},
        }
        try:
            result = await self._chat(payload)
            content = result.get("message", {}).get("content", "")
        except (httpx.HTTPError, ValueError, TypeError) as error:
            LOGGER.warning("model_router classifier_fallback reason=%s", type(error).__name__)
            return "chat"

        label = str(content).strip().lower().split()[0] if str(content).strip() else "chat"
        return label if label in VALID_CATEGORIES else "chat"

    async def _unload(self, model: str) -> None:
        payload = {"model": model, "messages": [], "stream": False, "keep_alive": 0}
        try:
            await self._chat(payload)
            LOGGER.info("model_router unloaded model=%s", model)
        except httpx.HTTPError as error:
            LOGGER.warning("model_router unload_failed model=%s reason=%s", model, type(error).__name__)

    async def _chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=10.0)) as client:
            response = await client.post(f"{self.valves.OLLAMA_BASE_URL.rstrip('/')}/api/chat", json=payload)
            response.raise_for_status()
            return response.json()

    async def _stream_chat(self, payload: dict[str, Any]) -> AsyncIterator[str]:
        url = f"{self.valves.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(None, connect=10.0)) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line)
                        text = chunk.get("message", {}).get("content", "")
                        if text:
                            yield self._sse_delta(text)
                        if chunk.get("done"):
                            yield "data: [DONE]\n\n"
        except (httpx.HTTPError, json.JSONDecodeError) as error:
            yield self._sse_error(f"Ollama request failed: {type(error).__name__}")
            yield "data: [DONE]\n\n"

    @staticmethod
    def _messages(body: dict[str, Any]) -> list[dict[str, Any]]:
        messages = body.get("messages", [])
        if not isinstance(messages, list):
            return []
        return [message for message in messages if isinstance(message, dict) and message.get("role")]

    @staticmethod
    def _latest_user_text(messages: list[dict[str, Any]]) -> str:
        for message in reversed(messages):
            if message.get("role") == "user":
                content = message.get("content", "")
                return content if isinstance(content, str) else ""
        return ""

    @staticmethod
    def _session_key(body: dict[str, Any], user: dict[str, Any] | None) -> str:
        for key in ("chat_id", "conversation_id", "session_id"):
            if body.get(key):
                return f"chat:{body[key]}"
        if user and user.get("id"):
            return f"user:{user['id']}"
        return "local:default"

    @staticmethod
    def _sse_delta(text: str) -> str:
        data = {"choices": [{"delta": {"content": text}, "index": 0, "finish_reason": None}]}
        return f"data: {json.dumps(data)}\n\n"

    @staticmethod
    def _sse_error(message: str) -> str:
        return f"data: {json.dumps({'error': {'message': message}})}\n\n"
