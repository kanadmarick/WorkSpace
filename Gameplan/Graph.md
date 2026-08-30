# Graph

## Purpose

This document describes the conceptual graph of the career execution system. The graph captures how work products, phases, outputs, and skills connect to each other.

## Core nodes

- Career target
- Portfolio domains
- Roadmap phases
- Deliverables
- Evidence
- Interview answers
- Models for review

## Key relationships

### Career target -> portfolio domains

The target role influences how each portfolio domain is framed.

- Sentinel: safe operations and remediation
- Hadron/Aether: inference and model-serving architecture
- Zenith: analytics and market-facing decision support

### Portfolio domain -> deliverables

Each portfolio area contributes to specific engineering artifacts.

- infrastructure
- observability
- messaging
- model routing
- resilience testing

### Deliverables -> evidence

Every deliverable should produce visible proof:

- code repository
- design doc
- diagrams
- benchmark or load test
- demo or recorded walkthrough
- incident or failure analysis

### Phase -> interview readiness

Each roadmap phase ends with a form of interview preparation:

- architecture explanation
- trade-off defense
- failure-mode discussion
- metric-based rationale

## Example graph structure

```text
Career Target
  ├── Sentinel
  │     ├── Infrastructure isolation
  │     ├── Action controls
  │     └── Audit trail
  ├── Hadron/Aether
  │     ├── Inference gateway
  │     ├── Prompt logging
  │     └── Fallback design
  └── Zenith
        ├── Data constraints
        ├── Analysis workflow
        └── Chaos validation

Roadmap Phases -> Deliverables -> Evidence -> Interview Readiness
```

## Model review graph

Local models can be used as different reviewers:

- qwen3:8b -> design critique and implementation review
- llama3.1:8b -> challenge assumptions and reliability thinking
- mistral:7b -> ADR and concise interview review
- Nemotron-Flash-1B -> triage or classification experiments

This creates a small review network, allowing structured independent feedback without cloud dependence.

## Summary

The graph is not a database schema; it is a conceptual model that explains how the project progresses from role target to portfolio evidence to interview readiness.
