#!/usr/bin/env python3
"""Small local web UI to list installed Ollama models and switch the active one."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import urllib.request

from router_pipe import classify_question, route_question

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
INDEX_PATH = ROOT / "index.html"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_config(config: dict) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")


def guess_category(name: str) -> str:
    lowered = name.lower()
    if "coder" in lowered or "code" in lowered:
        return "code"
    if "r1" in lowered or "math" in lowered or "reason" in lowered:
        return "math"
    if "mistral" in lowered or "write" in lowered:
        return "writing"
    if "llava" in lowered or "vision" in lowered:
        return "vision"
    if "embed" in lowered:
        return "embedding"
    return "chat"


def merge_models(config: dict, live_models: list[dict]) -> list[dict]:
    catalog = {entry.get("name"): entry for entry in config.get("available_models", []) if isinstance(entry, dict) and entry.get("name")}
    merged = []
    seen = set()

    for model in live_models:
        name = model.get("name") or model.get("model")
        if not name or name in seen:
            continue
        seen.add(name)
        category = catalog.get(name, {}).get("category") or guess_category(name)
        merged.append({"name": name, "category": category})

    for entry in config.get("available_models", []):
        name = entry.get("name")
        if not name or name in seen:
            continue
        seen.add(name)
        merged.append({"name": name, "category": entry.get("category", guess_category(name))})

    return merged


def get_live_models(base_url: str) -> list[dict]:
    url = f"{base_url.rstrip('/')}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (Exception, ValueError):
        return []

    models = payload.get("models", [])
    return [
        {
            "name": item.get("name") or item.get("model"),
            "category": item.get("category") or guess_category(item.get("name") or item.get("model") or ""),
        }
        for item in models
        if item.get("name") or item.get("model")
    ]


def get_models_response() -> dict:
    config = load_config()
    live_models = get_live_models(config.get("ollama_base_url", "http://127.0.0.1:11434"))
    models = merge_models(config, live_models)
    selected = config.get("selected_model")
    if selected and selected not in {item["name"] for item in models}:
        selected = models[0]["name"] if models else None
        config["selected_model"] = selected
        save_config(config)
    return {
        "selected_model": selected,
        "models": models,
    }


class ModelSwitcherHandler(BaseHTTPRequestHandler):
    server_version = "ModelSwitcher/1.0"

    def do_HEAD(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_file(INDEX_PATH, head_only=True)
            return

        if path in {"/api/models", "/api/config"}:
            payload = get_models_response() if path == "/api/models" else load_config()
            self._send_json(payload, head_only=True)
            return

        self.send_error(404, "Not found")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_file(INDEX_PATH)
            return

        if path == "/api/models":
            self._send_json(get_models_response())
            return

        if path == "/api/config":
            self._send_json(load_config())
            return

        if path == "/api/route-question":
            question = parse_qs(parsed.query).get("question", [""])[0]
            if not question:
                self.send_error(400, "question query parameter is required")
                return

            route = route_question(question)
            self._send_json({"status": "ok", **route})
            return

        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/select-model":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return

            model_name = payload.get("model")
            if not model_name:
                self.send_error(400, "model is required")
                return

            config = load_config()
            models = get_models_response()["models"]
            names = {item["name"] for item in models}
            if model_name not in names:
                self.send_error(400, f"Unknown model: {model_name}")
                return

            config["selected_model"] = model_name
            selected_entry = next(item for item in models if item["name"] == model_name)
            config.setdefault("category_models", {})
            config["category_models"][selected_entry["category"]] = model_name
            config["available_models"] = models
            save_config(config)

            self._send_json({"status": "ok", "selected_model": model_name})
            return

        if parsed.path == "/api/route-question":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return

            question = payload.get("question") or payload.get("prompt") or payload.get("text") or ""
            if not question:
                self.send_error(400, "question is required")
                return

            route = route_question(question)
            category = classify_question(question)
            route["category"] = category
            self._send_json({"status": "ok", **route})
            return

        self.send_error(404, "Not found")

    def _serve_file(self, file_path: Path, head_only: bool = False):
        try:
            content = file_path.read_bytes()
        except FileNotFoundError:
            self.send_error(404, "File not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if not head_only:
            self.wfile.write(content)

    def _send_json(self, payload: dict, head_only: bool = False):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8765
    server = ThreadingHTTPServer((host, port), ModelSwitcherHandler)
    print(f"Serving model switcher at http://{host}:{port}/")
    server.serve_forever()
