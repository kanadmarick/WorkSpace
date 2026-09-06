# Model routing guide

This project uses a small model for quick classification and then routes the real task to the model that best matches both the request type and the task complexity.

Use the smallest model that can do the job well. Short, easy prompts should stay on the lighter model. Harder prompts, deeper reasoning, longer writing, or complex debugging should move up to the bigger model.

## Recommended routing

- Code: best on `qwen2.5-coder:7b` for real implementation, debugging, and API work. For short helper tasks or quick one-liners, use `qwen2.5:3b`.
- Chat: best on `qwen3:8b` for open-ended conversation. For simple Q&A or lightweight replies, use `llama3.2:3b`.
- Math: best on `deepseek-r1:7b` for proofs, symbolic work, and hard reasoning. For short arithmetic or quick checks, use `qwen2.5:3b`.
- Writing: best on `mistral:7b` for rewrites, essays, and polished long-form writing. For quick edits or simple drafting, use `llama3.2:3b`.

## Selection rules

- If the question is short, direct, and low-risk, prefer the smaller model.
- If the question is long, multi-step, or requires deep reasoning, choose the larger model in that bucket.
- If the request clearly asks for code, debugging, or API changes, route to code.
- If it is a calculation, proof, or derivation, route to math.
- If it is rewriting, storytelling, or editing text, route to writing.
- Otherwise route to chat.

<!-- model-routing-config:start -->
{
  "code": {
    "easy": "qwen2.5:3b",
    "default": "qwen2.5-coder:7b"
  },
  "chat": {
    "easy": "llama3.2:3b",
    "default": "qwen3:8b"
  },
  "math": {
    "easy": "qwen2.5:3b",
    "default": "deepseek-r1:7b"
  },
  "writing": {
    "easy": "llama3.2:3b",
    "default": "mistral:7b"
  }
}
<!-- model-routing-config:end -->
