"""Career execution tracker for the Senior AI Backend Engineer pivot."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).parent
STATE_FILE = ROOT / "progress.json"

CAREER_PROFILE = {
    "target_role": "Senior/Lead AI Backend Engineer",
    "compensation_goal": "40 LPA",
    "timeline": "6-9 months",
    "weekly_hours": "10-12 focused hours",
    "markets": "India product companies, global remote roles, and startups",
}

PHASES = [
    {
        "name": "Phase 0: Positioning",
        "duration": "Week 1",
        "outcome": "A credible Senior AI Backend Engineer narrative and measurable baseline.",
        "deliverables": [
            "One-page architecture brief for Sentinel, Hadron/Aether, and Zenith.",
            "Resume bullet bank translating Linux, DevOps, and Python work into scale, reliability, and ownership.",
            "Public GitHub standards: ADRs, diagrams, tests, CI, threat model, and runbooks.",
        ],
        "interview_question": "Explain why your DevOps background is an advantage for AI backend engineering rather than a career switch risk.",
    },
    {
        "name": "Phase 1: Infrastructure Bunker",
        "duration": "Weeks 2-4",
        "outcome": "Reproducible and isolated Kubernetes platform for the portfolio ecosystem.",
        "deliverables": [
            "Terraform modules with environment-separated state and remote state locking.",
            "Namespaces: platform-system, observability, messaging, sentinel, hadron, and zenith.",
            "Default-deny network policies, workload identities, resource quotas, and secret-management design.",
        ],
        "interview_question": "How would you isolate a self-healing remediation agent so it cannot gain cluster-admin or unrestricted SSH access?",
    },
    {
        "name": "Phase 2: Streaming and Observability",
        "duration": "Weeks 5-6",
        "outcome": "Replayable telemetry and traceable operations from event to remediation.",
        "deliverables": [
            "Kafka event contracts with schema versioning, idempotency keys, retries, and dead-letter handling.",
            "OpenTelemetry traces, Prometheus SLOs, dashboards, structured logs, and alert runbooks.",
            "Load test demonstrating throughput, lag behavior, and failure recovery.",
        ],
        "interview_question": "Why use Kafka rather than RabbitMQ for durable server telemetry, and where would RabbitMQ still be a better choice?",
    },
    {
        "name": "Phase 3: Sentinel and Aether",
        "duration": "Weeks 7-10",
        "outcome": "Safe agentic operations with local-model inference and human-controlled remediation.",
        "deliverables": [
            "Pydantic v2 API contracts, Celery/Redis worker boundaries, action allowlists, and audit trail.",
            "Anomaly pipeline with offline evaluation, precision/recall targets, and false-positive controls.",
            "Inference gateway with model routing, timeouts, concurrency limits, prompt/version logging, and fallbacks.",
        ],
        "interview_question": "Design idempotent remediation for a flapping server alert while preserving an auditable decision trail.",
    },
    {
        "name": "Phase 4: Zenith and Resilience Proof",
        "duration": "Weeks 11-12",
        "outcome": "A useful consuming product and evidence that the platform survives controlled failures.",
        "deliverables": [
            "Market-data pipeline with explicit data-source limits and no financial-advice claims.",
            "Chaos experiments for pod loss, latency, and Kafka consumer failure, each with a steady-state hypothesis.",
            "Recorded demo: incident, detection, reasoned proposal, approval or policy gate, remediation, and recovery proof.",
        ],
        "interview_question": "What steady-state hypothesis must be defined before injecting chaos, and how do you stop an experiment safely?",
    },
    {
        "name": "Phase 5: Hiring Loop",
        "duration": "Weeks 13-16",
        "outcome": "Interview-ready portfolio and a repeatable senior-level job-search process.",
        "deliverables": [
            "Three case studies with architecture trade-offs, cost/capacity assumptions, and incidents avoided.",
            "Weekly system-design, Python backend, Kubernetes, Kafka, and MLOps mock interviews.",
            "Target-company tracker, referral outreach, and post-interview improvement log.",
        ],
        "interview_question": "Walk through the hardest architecture trade-off in Sentinel and defend the decision using reliability, cost, and security constraints.",
    },
]


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"completed": [], "evidence": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def show_roadmap() -> None:
    state = load_state()
    completed = set(state["completed"])
    for index, phase in enumerate(PHASES, start=1):
        marker = "[x]" if index in completed else "[ ]"
        print(f"{marker} {index}. {phase['name']} ({phase['duration']})")
        print(f"    Outcome: {phase['outcome']}")
        for deliverable in phase["deliverables"]:
            print(f"    - {deliverable}")


def show_next_step() -> None:
    state = load_state()
    completed = set(state["completed"])
    for index, phase in enumerate(PHASES, start=1):
        if index not in completed:
            print(f"Next: {phase['name']} ({phase['duration']})")
            print(phase["outcome"])
            print("This week's evidence:")
            for deliverable in phase["deliverables"]:
                print(f"- {deliverable}")
            return
    print("All roadmap phases are marked complete. Focus on interview feedback and targeted applications.")


def show_execution_cadence() -> None:
    print(f"Target: {CAREER_PROFILE['target_role']} at {CAREER_PROFILE['compensation_goal']}")
    print(f"Runway: {CAREER_PROFILE['timeline']} | Capacity: {CAREER_PROFILE['weekly_hours']}")
    print(f"Search: {CAREER_PROFILE['markets']}\n")
    print("Months 1-2: Build the infrastructure and streaming foundation; publish one ADR and one demo each week.")
    print("Months 3-4: Deliver Sentinel/Aether safety, observability, and load-test proof; begin 3 targeted applications weekly.")
    print("Months 5-6: Complete Zenith and chaos validation; begin 2 mocks weekly and 5 targeted applications weekly.")
    print("Months 7-9: Use interview feedback to deepen weak areas; maintain applications, referrals, and one portfolio improvement per week.")
    print("Weekly split: 6 hours implementation, 2 hours architecture/ADRs, 2 hours interview practice, 1-2 hours outreach and applications.")


def complete_phase(number: int) -> None:
    if number < 1 or number > len(PHASES):
        raise SystemExit(f"Phase must be between 1 and {len(PHASES)}.")
    state = load_state()
    if number not in state["completed"]:
        state["completed"].append(number)
        state["completed"].sort()
        save_state(state)
    print(f"Marked phase {number} complete.")


def add_evidence(text: str) -> None:
    state = load_state()
    state["evidence"].append({"date": date.today().isoformat(), "note": text})
    save_state(state)
    print("Evidence recorded.")


def show_evidence() -> None:
    evidence = load_state()["evidence"]
    if not evidence:
        print("No evidence recorded yet. Add a deployed feature, ADR, benchmark, test report, or demo link.")
        return
    for item in evidence:
        print(f"{item['date']}: {item['note']}")


def ask_interview_question() -> None:
    state = load_state()
    completed = set(state["completed"])
    phase_number = next((index for index in range(1, len(PHASES) + 1) if index not in completed), len(PHASES))
    phase = PHASES[phase_number - 1]
    print(f"40 LPA interview question - {phase['name']}:\n{phase['interview_question']}")
    print("Answer structure: context and constraints -> alternatives -> decision -> failure modes -> metrics and trade-offs.")


def main() -> None:
    parser = argparse.ArgumentParser(description="40 LPA AI Backend Engineer execution tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("roadmap", help="show the full 16-week plan")
    subparsers.add_parser("next", help="show the current phase and its evidence targets")
    subparsers.add_parser("cadence", help="show the 6-9 month execution and job-search cadence")
    complete_parser = subparsers.add_parser("complete", help="mark a phase complete")
    complete_parser.add_argument("phase", type=int)
    evidence_parser = subparsers.add_parser("evidence", help="record a portfolio evidence item")
    evidence_parser.add_argument("note")
    subparsers.add_parser("evidence-log", help="show recorded evidence")
    subparsers.add_parser("interview", help="generate a focused senior-level interview question")
    args = parser.parse_args()

    if args.command == "roadmap":
        show_roadmap()
    elif args.command == "next":
        show_next_step()
    elif args.command == "cadence":
        show_execution_cadence()
    elif args.command == "complete":
        complete_phase(args.phase)
    elif args.command == "evidence":
        add_evidence(args.note)
    elif args.command == "evidence-log":
        show_evidence()
    else:
        ask_interview_question()


if __name__ == "__main__":
    main()