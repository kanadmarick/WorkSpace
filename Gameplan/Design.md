# Design

## Purpose

Gameplan is a lightweight career-execution system for a senior AI backend engineer transition. It helps a user turn a broad goal into a structured roadmap, weekly execution cadence, evidence log, and interview-ready prompts.

The system is intentionally simple: a Python CLI plus a local dashboard. It avoids cloud dependencies and keeps all planning in a local, reviewable format.

## Core design principles

- Evidence over aspiration: a phase is only complete when there is proof.
- Local-first operation: no cloud APIs required for core flow.
- Strong architecture framing: every artifact is tied to production engineering constraints.
- Weekly focus: narrow milestones that fit a 10-12 hour schedule.
- Portfolio coherence: Sentinel, Hadron/Aether, and Zenith all reinforce the same target narrative.

## Functional model

### 1. Roadmap engine

The CLI in `gameplan.py` exposes staged phases such as:

- Positioning
- Infrastructure Bunker
- Streaming and Observability
- Sentinel and Aether
- Zenith and Resilience Proof
- Hiring Loop

Each phase includes:

- duration
- outcome
- deliverables
- interview question

The CLI can show the roadmap, show the next phase, mark a phase complete, record evidence, and produce an interview question.

### 2. State persistence

The application stores progress in a local JSON file, `progress.json`, adjacent to the script. This keeps the plan portable and easy to inspect in Git or a local workspace.

State includes:

- completed phases
- evidence log entries
- timestamps

### 3. Dashboard

The local dashboard in `server.py` serves a static UI from the `ui/` directory. It provides a browser-based view of status and feedback, and it can route mentorship prompts to local Ollama models.

This is intentionally designed for privacy and speed:

- no external service calls
- local model routing only
- small prompt envelope with structured context

## System boundaries

### Inbound

- user commands from CLI
- browser requests for dashboard or model review
- local evidence entries

### Core

- roadmap definition
- progress tracking
- evidence registry
- local model routing

### Outbound

- terminal output
- browser dashboard actions
- local model responses via Ollama

## Non-functional considerations

### Reliability

- minimal moving parts
- file-based state
- no external database required

### Security

- model prompt is limited in size
- allowed models are fixed
- prompt content is contextualized but not arbitrary system-level access

### Maintainability

- docs are explicit and human-readable
- phases are structured data instead of hidden logic
- evidence format is simple and audit-friendly

## Extension points

Future enhancements could include:

- richer charting for phase completion
- trend analysis over evidence entries
- custom role profiles
- per-phase checklist with attachments
- export to markdown or PDF

## Summary

The design favors a transparent process over an elaborate product. It is a planning and evidence system for career execution, and it makes the user’s progress auditable, reviewable, and grounded in real artifacts.
