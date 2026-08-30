const phases = [
  { title: "Positioning", duration: "Week 1", outcome: "Turn Linux, DevOps, and Python depth into a credible AI-backend ownership narrative.", evidence: ["Architecture brief for the Portfolio Trinity", "Resume bullet bank with scale and reliability metrics", "Public GitHub standards for ADRs, tests, CI, and runbooks"], question: "Explain why your DevOps background is an advantage for AI backend engineering rather than a career-switch risk." },
  { title: "Infrastructure Bunker", duration: "Weeks 2–4", outcome: "Provision an isolated and reproducible Kubernetes platform.", evidence: ["Terraform modules and environment-separated state", "Namespaces, quotas, workload identities, and default-deny policy", "Secrets-management and cluster threat-model ADR"], question: "How would you isolate a self-healing remediation agent so it cannot gain cluster-admin or unrestricted SSH access?" },
  { title: "Streaming and Observability", duration: "Weeks 5–6", outcome: "Build replayable telemetry and traceable operations.", evidence: ["Versioned Kafka event contracts", "SLO dashboard and OpenTelemetry traces", "Load-test report with consumer-lag recovery"], question: "Why choose Kafka rather than RabbitMQ for durable telemetry, and where is RabbitMQ the better choice?" },
  { title: "Sentinel and Aether", duration: "Weeks 7–10", outcome: "Deliver safe agentic operations with local-model inference.", evidence: ["Pydantic v2 contracts and action allowlists", "Anomaly evaluation with false-positive controls", "Inference gateway with timeouts and routing"], question: "Design idempotent remediation for a flapping alert while preserving a complete auditable decision trail." },
  { title: "Zenith and Resilience Proof", duration: "Weeks 11–12", outcome: "Prove useful business value and resilience under controlled faults.", evidence: ["Market-data pipeline with source limits", "Chaos experiment reports", "Incident-to-recovery demo recording"], question: "What steady-state hypothesis must exist before chaos injection, and how do you stop the experiment safely?" },
  { title: "Hiring Loop", duration: "Weeks 13–16", outcome: "Convert portfolio proof into high-quality interview performance.", evidence: ["Three architectural case studies", "Mock interview feedback log", "Target-company and referral tracker"], question: "Defend Sentinel's hardest trade-off using reliability, cost, security, and operational constraints." }
];

const storageKey = "ai-backend-gameplan-v1";
const initialState = { complete: [], evidence: [] };
let state = JSON.parse(localStorage.getItem(storageKey)) || initialState;
let questionOffset = 0;

const persist = () => localStorage.setItem(storageKey, JSON.stringify(state));
const phaseList = document.querySelector("#phase-list");
const focusTitle = document.querySelector("#focus-title");
const focusOutcome = document.querySelector("#focus-outcome");
const focusItems = document.querySelector("#focus-items");

function currentPhase() {
  return phases.findIndex((_, index) => !state.complete.includes(index)) || 0;
}

function renderPhases() {
  phaseList.innerHTML = phases.map((phase, index) => {
    const done = state.complete.includes(index);
    return `<article class="phase-row ${done ? "done" : ""}">
      <span class="phase-index">${String(index + 1).padStart(2, "0")}</span>
      <div class="phase-copy"><h3>${phase.title}</h3><p>${phase.duration} · ${phase.outcome}</p></div>
      <button class="phase-toggle" data-phase="${index}" title="${done ? "Mark incomplete" : "Mark complete"}" aria-label="${done ? "Mark incomplete" : "Mark complete"} ${phase.title}"><i data-lucide="${done ? "check" : "circle"}"></i></button>
    </article>`;
  }).join("");
  document.querySelectorAll(".phase-toggle").forEach((button) => button.addEventListener("click", () => togglePhase(Number(button.dataset.phase))));
  document.querySelector("#phase-count").textContent = `${state.complete.length} / ${phases.length}`;
  document.querySelector("#progress-bar").style.width = `${state.complete.length / phases.length * 100}%`;
}

function renderFocus() {
  const phase = phases[currentPhase()];
  focusTitle.textContent = `Phase ${currentPhase() + 1}: ${phase.title}`;
  focusOutcome.textContent = phase.outcome;
  focusItems.innerHTML = phase.evidence.map((item) => `<li>${item}</li>`).join("");
}

function renderEvidence() {
  const list = document.querySelector("#evidence-list");
  document.querySelector("#evidence-count").textContent = state.evidence.length;
  list.innerHTML = state.evidence.length
    ? state.evidence.slice().reverse().map((item) => `<article class="evidence-item"><time>${item.date}</time><p>${escapeHtml(item.note)}</p></article>`).join("")
    : `<p class="empty-evidence">Record the work that proves senior-level ownership: deployed services, ADRs, benchmark reports, resilience drills, and interview feedback.</p>`;
}

function renderQuestion() {
  const phase = phases[(currentPhase() + questionOffset) % phases.length];
  document.querySelector("#interview-question").textContent = phase.question;
}

function togglePhase(index) {
  state.complete = state.complete.includes(index) ? state.complete.filter((item) => item !== index) : [...state.complete, index].sort((a, b) => a - b);
  persist();
  render();
}

function escapeHtml(value) {
  return value.replace(/[&<>"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[character]);
}

function render() {
  renderPhases();
  renderFocus();
  renderEvidence();
  renderQuestion();
  lucide.createIcons();
}

document.querySelector("#evidence-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = document.querySelector("#evidence-input");
  state.evidence.push({ date: new Date().toLocaleDateString("en-CA"), note: input.value.trim() });
  input.value = "";
  persist();
  renderEvidence();
});

document.querySelector("#new-question").addEventListener("click", () => {
  questionOffset = (questionOffset + 1) % phases.length;
  renderQuestion();
});

document.querySelector("#mentor-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.querySelector("#mentor-input");
  const button = document.querySelector("#mentor-submit");
  const answer = document.querySelector("#mentor-answer");
  answer.textContent = "Local model is reviewing your request...";
  answer.classList.add("loading");
  button.disabled = true;

  try {
    const response = await fetch("/api/mentor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: document.querySelector("#model-select").value, prompt: input.value.trim() })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || "The local model did not return a response.");
    answer.textContent = data.answer;
  } catch (error) {
    answer.textContent = `Review unavailable: ${error.message}`;
  } finally {
    answer.classList.remove("loading");
    button.disabled = false;
  }
});

render();