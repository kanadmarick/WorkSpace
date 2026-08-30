# Prompt

## Purpose

This file documents the kinds of prompts that should be used with the local mentorship workflow. The prompts are designed to push the user toward practical, senior-level architecture decisions and realistic career execution.

## Prompt pattern

A good prompt should include:

- context about the current phase
- the target role
- the constraints in play
- the decision to evaluate
- the expected output style

## Example prompt templates

### Architecture review

```text
Review my current design for Sentinel with a focus on security, observability, and failure isolation. Identify the top three risks and propose the next design change that would most improve production readiness.
```

### Trade-off analysis

```text
Compare Kafka vs RabbitMQ for durable server telemetry in a self-healing SRE system. Use throughput, replayability, operational complexity, and failure recovery in the answer.
```

### Interview readiness

```text
I am preparing for a Senior AI Backend Engineer interview. Give me a concise answer to: 'How do you isolate an autonomous remediation agent so it cannot gain cluster-admin access?' Focus on design constraints and trade-offs.
```

### Career execution

```text
I have 10-12 focused hours per week for the next 16 weeks. Suggest the best next action for my portfolio plan, aligned to a 40 LPA Senior AI Backend Engineer target role.
```

## Prompt quality rules

- Ask for constraints before solutions.
- Require trade-offs and failure modes.
- Favor concrete next steps over generalized advice.
- Keep answers brief but technical.
- Tie recommendations back to portfolio evidence.

## Model-specific use

- qwen3:8b: architecture and design refinement
- llama3.1:8b: challenge assumptions and risk analysis
- mistral:7b: ADR and concise interview policy review

## Summary

The prompt system is not meant to replace thinking. It is meant to sharpen thinking and turn the project into a structured, evidence-driven execution loop.
