# Memory

## Purpose

This document defines how the gameplan keeps track of state, learning, and evidence over time. In this project, memory is intentionally lightweight and observable.

## Memory types

### 1. Execution memory

Execution memory records the current state of the roadmap.

Example fields:

- completed phases
- next recommended phase
- weekly cadence summary
- tracked evidence items

This is stored in `progress.json` and is the primary operational memory for the project.

### 2. Evidence memory

Evidence memory stores proof that work is real, not merely planned.

Examples:

- ADR published
- test artifact generated
- architecture review done
- demo recorded
- incident postmortem created

Evidence is timestamped and kept in a human-readable list so it can be reviewed later.

### 3. Narrative memory

Narrative memory captures the story behind the portfolio:

- target role
- domain framing
- technical strengths
- reliability and security story
- market positioning

This helps ensure that the project is not just building systems but also building an interview-ready identity.

## Memory lifecycle

1. Plan phase
2. Execute work
3. Capture evidence
4. Review outcome
5. Update next step

## Memory rules

- Memory should be explicit, not hidden in code-only assumptions.
- Evidence should be reviewable by humans.
- A phase is incomplete until it has a traceable artifact.
- A system design should be grounded in constraint-based reasoning, not confidence alone.

## Example memory structure

```json
{
  "completed": [1, 2],
  "evidence": [
    {
      "date": "2026-08-24",
      "note": "Published Sentinel namespace isolation ADR"
    }
  ]
}
```

## Operational guidance

When using the CLI:

- run `next` to see what the next phase requires
- run `evidence` after each meaningful artifact
- review the evidence log before claiming completion
- keep notes in a form that maps directly to portfolio deliverables

## Summary

Memory in this project is not an abstract agent concept. It is a disciplined operational record that links intent, execution, and proof.
