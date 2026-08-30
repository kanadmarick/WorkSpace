# Training Gate

## Current decision

Do not fine-tune a model for the 6-9 month career-coaching goal yet. The desired guidance changes each week as portfolio evidence, interview feedback, and target roles evolve. Use Qwen3 8B through the local mentor dashboard with the career context embedded in the prompt.

Use human review as the success mechanism for weekly plans:

1. Record the week's evidence in the dashboard.
2. Ask Qwen3 for the next highest-leverage action.
3. Challenge it with Llama 3.1 or Mistral when the decision has security, architecture, or career impact.
4. Keep only advice that results in an observable artifact, application, interview improvement, or measurable learning outcome.

## Fine-tune later, only for a stable behavior

Fine-tuning becomes appropriate after you select one repeatable task, such as SRE incident triage JSON, architecture-review scoring, or code-review finding extraction. Create 100-300 de-identified, human-reviewed examples and keep 20% aside for evaluation before training.

The first acceptance criterion must compare base and tuned outputs on held-out examples. Human review should score schema validity, factual grounding, safety, and usefulness. Do not train on private tickets, credentials, SSH output, or other secrets.