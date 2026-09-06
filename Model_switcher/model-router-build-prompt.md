# Build Prompt: Task-Aware Ollama Model Router (Open WebUI Pipe)

## Context

I run Ollama locally on a Lenovo Legion 5 (Ryzen 7 4800H, 32GB RAM, NVIDIA GTX 1660Ti — 6GB VRAM), on Fedora Linux. I have multiple Ollama models pulled, all under 8B parameters, covering different strengths: code, general chat, math/reasoning, and writing.

I want a single "smart" model in Open WebUI that automatically routes each message to the best underlying Ollama model based on the type of task, instead of me manually switching models.

## Goal

Build an Open WebUI **Pipe function** (Python) that:

1. Classifies each incoming user message into a task category using a small, fast classifier model
2. Routes the message to the appropriate task-specific Ollama model for that category
3. Is "sticky" — reuses the currently loaded model if the new message is the same category as the previous turn, and only swaps models when the category actually changes
4. Streams the task model's response back to Open WebUI like a normal chat

## Hardware constraints (important)

- Only 6GB VRAM — can realistically hold one ~7B Q4 model on GPU at a time
- The classifier model must run on **CPU only** (`num_gpu: 0`) so it doesn't compete for VRAM with the task model
- The task model must run on **GPU** (`num_gpu: -1` or equivalent "max" setting)
- Model swaps have a real cost (load time), so avoid unnecessary reloading — this is the reason for the sticky/hysteresis logic

## Architecture

```
Open WebUI → Pipe function
  1. Classify (Ollama call, CPU-pinned, small model e.g. phi3:3.8b or qwen2.5:3b)
     → strict single-word category output
  2. Compare to session's current_category
     - same → reuse already-loaded task model
     - different → call task model with GPU options (Ollama will load it; previous
       task model will idle/unload per keep_alive settings)
  3. Call task model (Ollama, GPU-pinned) with full conversation history
  4. Stream response back to Open WebUI
```

## Requirements for the classifier

- Categories: `code`, `chat`, `math`, `writing` (default/fallback: `chat`)
- System prompt must force a single-word category label as output, nothing else
- Runs against a small model (e.g. `phi3:3.8b` or `qwen2.5:3b`) via Ollama's API with `options: {num_gpu: 0}`
- Should look at the latest user message (and optionally recent context) — not the entire history — to keep classification fast

## Requirements for routing/state

- Maintain per-session state: `current_category`, `current_model`
- Config should be an editable mapping (JSON or YAML) of category → Ollama model name, e.g.:
  ```json
  {
    "code": "qwen2.5-coder:7b",
    "chat": "llama3.1:8b",
    "math": "qwen2.5-math:7b",
    "writing": "mistral:7b"
  }
  ```
- On category change, explicitly set `keep_alive` appropriately so the old GPU model unloads and the new one loads cleanly (avoid VRAM overrun)
- Log every classification decision and swap event (category, model chosen, swapped y/n) for debugging/tuning

## Requirements for the task model call

- Use `options: {num_gpu: -1}` (or the correct Ollama option for "use GPU fully") for the task model call
- Pass the full conversation history (not just the latest message) to the task model
- Support streaming responses back through the Pipe so Open WebUI shows tokens as they arrive

## Deliverables

1. `config.json` (or `.yaml`) — category → model mapping, easily editable
2. `router_pipe.py` — the Open WebUI Pipe function implementing the full flow above
3. A short classifier system prompt (as a constant or config value) that reliably forces single-word category output
4. Brief inline comments explaining the sticky/hysteresis logic and the CPU/GPU option split
5. A short README section (in code comments or a separate note) on:
   - How to install this as a Pipe in Open WebUI
   - How to edit the category → model mapping
   - How to change/add categories later

## Non-goals for this version

- No need for embedding-based classification — small LLM classifier only
- No need for a standalone FastAPI server — this should work as a native Open WebUI Pipe function
- No multi-user/multi-tenant considerations — single local user is fine

## Testing expectations

Please include a short manual test checklist (as comments or a markdown block) covering:
- A coding prompt → routes to code model
- A general chat prompt → routes to chat model
- A math prompt → routes to math model
- A writing prompt → routes to writing model
- Two consecutive same-category prompts → confirms no reload happens (sticky behavior works)
- A category switch mid-conversation → confirms swap happens and old model unloads
