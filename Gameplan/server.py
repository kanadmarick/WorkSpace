"""Serve the local Gameplan dashboard without third-party dependencies."""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


HOST = "127.0.0.1"
PORT = 8765
UI_DIRECTORY = Path(__file__).parent / "ui"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
ALLOWED_MODELS = {"qwen3:8b", "llama3.1:8b", "mistral:7b"}
CAREER_CONTEXT = """
Career target: secure a 40 LPA Senior/Lead AI Backend Engineer role in 6-9 months.
Available capacity: 10-12 focused hours weekly.
Portfolio: Sentinel (safe self-healing SRE agent), Hadron/Aether (local inference and MaaS),
and Zenith (investment data and analytics). Target markets include India product companies,
global remote roles, and startups.
""".strip()


class GameplanHandler(SimpleHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/mentor":
            self.send_error(404, "Not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > 24_000:
            self.send_error(413, "Prompt is too large")
            return

        try:
            request_data = json.loads(self.rfile.read(content_length))
            model = request_data["model"]
            prompt = request_data["prompt"].strip()
        except (json.JSONDecodeError, KeyError, AttributeError):
            self.send_error(400, "Expected model and prompt")
            return

        if model not in ALLOWED_MODELS or not prompt:
            self.send_error(400, "Invalid model or empty prompt")
            return

        mentor_prompt = (
            "You are a strict Lead Principal AI Architect mentoring a systems engineer toward a "
            "Senior/Lead AI Backend Engineer role. Prioritize production constraints: security, "
            "reliability, observability, capacity, failure modes, and measurable evidence. "
            "Do not produce toy designs. Be concise and constructive. For career planning, turn "
            "advice into a concrete next action that fits the weekly capacity.\n\n"
            f"Career context:\n{CAREER_CONTEXT}\n\n"
            f"Mentor request:\n{prompt}"
        )
        payload = json.dumps(
            {"model": model, "prompt": mentor_prompt, "stream": False, "options": {"temperature": 0.2}}
        ).encode()

        try:
            upstream = Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
            with urlopen(upstream, timeout=180) as response:
                answer = json.loads(response.read())["response"]
        except (URLError, TimeoutError, json.JSONDecodeError, KeyError) as error:
            self.send_error(502, f"Local model unavailable: {error}")
            return

        response = json.dumps({"answer": answer}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def main() -> None:
    handler = lambda *args, **kwargs: GameplanHandler(*args, directory=UI_DIRECTORY, **kwargs)
    server = ThreadingHTTPServer((HOST, PORT), handler)
    print(f"Gameplan dashboard: http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()