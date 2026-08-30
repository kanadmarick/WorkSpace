# 40 LPA Senior AI Backend Engineer Gameplan

This is an execution tracker for the Sentinel, Hadron/Aether, and Zenith portfolio ecosystem. It is deliberately evidence-driven: a completed phase needs deployed artifacts, tests, architecture decisions, and a demo, not only notes.

Run it from the workspace root:

```bash
uv run python Gameplan/gameplan.py roadmap
uv run python Gameplan/gameplan.py next
uv run python Gameplan/gameplan.py cadence
uv run python Gameplan/gameplan.py evidence "Published Sentinel namespace isolation ADR"
uv run python Gameplan/gameplan.py interview
```

## Dashboard

Run the local dashboard with:

```bash
uv run python Gameplan/server.py
```

Then open `http://127.0.0.1:8765`. Dashboard progress and evidence are stored in the browser on this machine.

The dashboard can also route a strict architecture-review prompt to Qwen3, Llama 3.1, or Mistral through the local Ollama service. It never sends prompts to a cloud service.

For the current 6-9 month career-coaching goal, use prompt context and weekly evidence rather than fine-tuning. The [training gate](TRAINING_GATE.md) defines when a later, narrow fine-tuning experiment is justified.

Start with `next`. Do not mark a phase complete until its deliverables have public, reviewable proof.

## Execution Constraint

The plan is configured for a 6-9 month search, 10-12 focused hours each week, and a mixed target market: India product companies, global remote roles, and startups. The 16-week roadmap is the technical core. The remaining time is deliberately reserved for case-study polish, targeted applications, referrals, and interview-feedback loops.

## Model Team

Use the local models sequentially:

- `qwen3:8b`: primary architecture proposal and implementation review.
- `llama3.1:8b`: independent challenge of security, scale, and failure assumptions.
- `mistral:7b`: ADR, test-plan, and concise interview-question reviewer.
- `Nemotron-Flash-1B`: small structured classifier for log/alert triage experiments, not principal architecture decisions.

Each component review should produce: an ADR, a threat model, an SLO, a load-test result, and one senior-level interview answer.