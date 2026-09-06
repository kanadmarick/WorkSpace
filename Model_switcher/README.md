# Smart Local Router for Open WebUI

This Open WebUI Pipe classifies the latest user message as `code`, `chat`, `math`, or `writing`, then sends the entire conversation to the configured Ollama model for that task.

The classifier uses `qwen2.5:1.5b` with `num_gpu: 0`, leaving the GPU available for one task model. Task models use `num_gpu: -1`. When a conversation category changes, the router unloads the previous task model with `keep_alive: 0` before loading the next one. Consecutive messages in the same category reuse the selected model.

## Install in Open WebUI

1. Open **Admin Panel** > **Functions** > **New Function**.
2. Set the function type to **Pipe**.
3. Copy the contents of `router_pipe.py` into the editor and save.
4. Enable the function, then select **Smart Local Router** from the model picker.
5. Ensure Open WebUI can reach Ollama at the configured `OLLAMA_BASE_URL`.

For Docker-based Open WebUI, `http://127.0.0.1:11434` usually points to the container itself. Set `OLLAMA_BASE_URL` to `http://host.docker.internal:11434` or your host LAN address instead.

## Configure Models

`config.json` is the development reference. After installation, edit the Pipe's Valves in Open WebUI and update `CATEGORY_MODELS_JSON`. If a configured task model is unavailable, the router automatically falls back to the `chat` model so the conversation still works:

```json
{
  "code": "qwen2.5-coder:7b",
  "chat": "qwen3:8b",
  "math": "deepseek-r1:7b",
  "writing": "mistral:7b"
}
```

Every mapping must include all four category names. To add a category, update `VALID_CATEGORIES`, `CLASSIFIER_PROMPT`, and the mapping together.

## Manual Test Checklist

- Ask for a Python bug fix and confirm logs show `category=code` and `qwen2.5-coder:7b`.
- Ask a general question and confirm `category=chat` and `qwen3:8b`.
- Ask a calculation or proof and confirm `category=math` and `deepseek-r1:7b`.
- Ask to rewrite a paragraph and confirm `category=writing` and `mistral:7b`.
- Send two code prompts consecutively and confirm the second log has `swapped=False`.
- Change from a code prompt to a writing prompt and confirm the previous code model is unloaded before the writing model responds.

## Model Switcher Web Page

A local model switcher page is included for quick manual switching between the Ollama models currently installed on this machine.

```bash
cd /home/kanadmarick/Workspace/Model_switcher
python model_switcher_server.py
```

Then open <http://127.0.0.1:8765/> in a browser. It lists every model returned by Ollama's `/api/tags` endpoint and lets you switch the active default model in `config.json`.

The same project also exposes a routing endpoint for code usage:

```bash
curl -X POST http://127.0.0.1:8765/api/route-question \
  -H 'Content-Type: application/json' \
  -d '{"question":"Fix this Python bug quickly"}'
```

Response example:

```json
{
  "status": "ok",
  "category": "code",
  "complexity": "easy",
  "model": "qwen2.5:3b"
}
```

This route will automatically prefer the smaller model on easier tasks and the larger model only when the request is more demanding.

## Local Validation

```bash
cd /home/kanadmarick/Workspace/Model_switcher
/home/kanadmarick/Workspace/.venv/bin/python -m unittest -v test_router.py
```
