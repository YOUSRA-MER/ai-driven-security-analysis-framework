import type {
  AssessmentReport,
  AssessmentResult,
  ReportFinding,
  ReportMetric,
  ReportPromptAnalysis,
  ReportSeverity,
  ReportTimelineItem,
} from "./reportModel";

export function generateAssessmentReport(result: AssessmentResult): AssessmentReport {
  const riskScore = Math.round(Math.min(Math.max(result.summary.maximum_heuristic_score, 0), 1) * 100);
  const confidence = result.planner ? Math.round(result.planner.confidence * 100) : 0;
  const promptAnalysis = buildPromptAnalysis(result);
  const findings = buildFindings(result, promptAnalysis);

  return {
    id: `report-${result.run_id}`,
    generatedAt: new Date().toISOString(),
    runId: result.run_id,
    title: `Assessment Report ${shortId(result.run_id)}`,
    executiveSummary: {
      verdict: verdictLabel(result.summary.heuristic_label),
      narrative: executiveNarrative(result, findings),
      riskScore,
      confidence,
      keyMetrics: [
        metric("Assessment status", sentence(result.status), result.phase),
        metric("Attack family", result.summary.attack_family || result.planner?.selected_attack_family || "Pending"),
        metric("Security signal", verdictLabel(result.summary.heuristic_label), `Maximum heuristic score ${result.summary.maximum_heuristic_score.toFixed(2)}`),
        metric("Execution coverage", `${result.summary.successful_turns}/${result.summary.total_turns} turns`, `${result.summary.failed_turns} failed`),
      ],
    },
    targetInformation: [
      metric("Provider", result.target.provider),
      metric("Model", result.target.model),
      metric("Endpoint", result.target.base_url),
      metric("Execution provider", result.execution?.provider ?? "Not executed"),
      metric("Execution model", result.execution?.model ?? "Not executed"),
    ],
    assessmentConfiguration: [
      metric("Objective", result.objective),
      metric("Preset", result.request?.objective_preset ? sentence(result.request.objective_preset) : "Unknown"),
      metric("Prompt variants", String(result.request?.prompt_count ?? result.summary.requested_prompts)),
      metric("Turn limit", String(result.request?.max_turns ?? result.summary.max_turns)),
      metric("Retries", String(result.request?.max_retries ?? result.execution?.execution_metrics.retry_count ?? 0)),
      metric("Timeout", result.request?.timeout_seconds ? `${result.request.timeout_seconds}s` : "Unknown"),
      metric("Temperature", result.request?.temperature?.toFixed(1) ?? "Unknown"),
      metric("Controlled baseline", result.request?.use_controlled_system_prompt ? "Enabled" : "Disabled"),
    ],
    timeline: buildTimeline(result),
    promptAnalysis,
    findings,
    evidence: buildEvidence(result, promptAnalysis),
    recommendations: buildRecommendations(result, findings),
    statistics: [
      metric("Coverage distribution", "Placeholder", "Reserved for future chart-free statistics."),
      metric("Finding trend", "Placeholder", "Reserved for future historical comparison."),
      metric("Control maturity", "Placeholder", "Reserved for future portfolio reporting."),
    ],
  };
}

function buildTimeline(result: AssessmentResult): ReportTimelineItem[] {
  const events = result.events ?? [];
  if (events.length === 0) {
    return [
      {
        label: "Assessment created",
        phase: result.phase,
        timestamp: result.created_at,
        level: "info",
        detail: result.status,
      },
    ];
  }
  return events.map((event) => ({
    label: event.message,
    phase: sentence(event.phase),
    timestamp: event.timestamp,
    level: event.level,
    detail: sentence(event.type),
  }));
}

function buildPromptAnalysis(result: AssessmentResult): ReportPromptAnalysis[] {
  const evaluations = new Map((result.heuristic_evaluation ?? []).map((evaluation) => [evaluation.turn_number, evaluation]));
  return (result.execution?.conversation_history ?? []).map((turn) => {
    const evaluation = evaluations.get(turn.turn_number);
    return {
      turnNumber: turn.turn_number,
      attackFamily: String(turn.metadata.attack_family ?? result.summary.attack_family ?? ""),
      strategy: String(turn.metadata.strategy_id ?? result.planner?.selected_strategy ?? ""),
      promptPreview: truncate(turn.prompt, 700),
      responsePreview: truncate(turn.response || "No response returned.", 700),
      status: turn.status,
      latencyMs: turn.latency_ms,
      evaluation,
      evidence: evaluation?.evidence ?? [],
    };
  });
}

function buildFindings(result: AssessmentResult, prompts: ReportPromptAnalysis[]): ReportFinding[] {
  const findings: ReportFinding[] = [];
  const vulnerableTurns = prompts.filter((prompt) => prompt.evaluation?.label === "vulnerable");
  const suspiciousTurns = prompts.filter((prompt) => prompt.evaluation?.label === "suspicious");
  const inconclusiveTurns = prompts.filter((prompt) => prompt.evaluation?.label === "inconclusive");

  if (vulnerableTurns.length > 0) {
    findings.push(finding({
      id: "finding-security-signal",
      title: "Security signal observed during target interaction",
      severity: severityFromScore(result.summary.maximum_heuristic_score),
      status: "observed",
      summary: "One or more completed turns produced heuristic evidence consistent with target control weakness.",
      affectedTurns: vulnerableTurns.map((turn) => turn.turnNumber),
      evidence: unique(vulnerableTurns.flatMap((turn) => turn.evidence)),
      recommendation: "Review the cited turns, reproduce the condition in a controlled environment, and strengthen the relevant instruction, retrieval, or data boundary.",
    }));
  }

  if (suspiciousTurns.length > 0) {
    findings.push(finding({
      id: "finding-suspicious-output",
      title: "Suspicious behavior requires analyst review",
      severity: "medium",
      status: "inconclusive",
      summary: "The assessment produced suspicious evidence but did not conclusively classify the target as vulnerable.",
      affectedTurns: suspiciousTurns.map((turn) => turn.turnNumber),
      evidence: unique(suspiciousTurns.flatMap((turn) => turn.evidence)),
      recommendation: "Re-run the assessment with a narrowed objective and inspect full prompts and responses for policy-boundary drift.",
    }));
  }

  if (result.execution?.errors.length) {
    findings.push(finding({
      id: "finding-execution-errors",
      title: "Execution reliability issues affected assessment coverage",
      severity: "low",
      status: "observed",
      summary: "Provider or runtime errors were recorded during execution and may reduce result completeness.",
      affectedTurns: result.execution.errors.map((error) => error.turn_number).filter((turn): turn is number => typeof turn === "number"),
      evidence: result.execution.errors.map((error) => error.message),
      recommendation: "Review provider availability, timeout settings, and retry configuration before comparing results across targets.",
    }));
  }

  if (findings.length === 0) {
    findings.push(finding({
      id: "finding-no-signal",
      title: "No qualifying security signal observed",
      severity: "informational",
      status: inconclusiveTurns.length > 0 ? "inconclusive" : "not_observed",
      summary: "The completed turns did not produce evidence that met the configured heuristic threshold for a vulnerability.",
      affectedTurns: [],
      evidence: inconclusiveTurns.flatMap((turn) => turn.evidence),
      recommendation: "Maintain the current controls and expand test coverage before treating this as a comprehensive assurance result.",
    }));
  }

  return findings;
}

function buildEvidence(result: AssessmentResult, prompts: ReportPromptAnalysis[]) {
  const evidence = prompts.flatMap((prompt) => [
    {
      id: `turn-${prompt.turnNumber}-prompt`,
      title: `Turn ${prompt.turnNumber} prompt`,
      detail: prompt.promptPreview,
    },
    {
      id: `turn-${prompt.turnNumber}-response`,
      title: `Turn ${prompt.turnNumber} response`,
      detail: prompt.responsePreview,
    },
  ]);
  for (const evaluation of result.heuristic_evaluation ?? []) {
    evidence.push({
      id: `turn-${evaluation.turn_number}-evaluation`,
      title: `Turn ${evaluation.turn_number} heuristic evidence`,
      detail: [evaluation.reason, ...evaluation.evidence].filter(Boolean).join("\n"),
    });
  }
  return evidence;
}

function buildRecommendations(result: AssessmentResult, findings: ReportFinding[]): AssessmentReport["recommendations"] {
  const hasObservedFinding = findings.some((finding) => finding.status === "observed" && finding.severity !== "informational");
  const attackFamily = (result.summary.attack_family || result.planner?.selected_attack_family || "").replace(/[_-]+/g, " ");
  return [
    {
      title: hasObservedFinding ? "Triage observed evidence" : "Preserve current controls",
      detail: hasObservedFinding
        ? "Assign an owner to review the affected turns, validate reproducibility, and decide whether the behavior is exploitable in the target deployment."
        : "Keep the current guardrails in place and use this report as a baseline for future regression assessments.",
      priority: hasObservedFinding ? "Immediate" : "Monitor",
    },
    {
      title: "Harden the tested control boundary",
      detail: `Focus remediation on ${attackFamily || "the selected attack family"} using the generated prompts, transcript, and heuristic evidence in this report.`,
      priority: hasObservedFinding ? "Immediate" : "Planned",
    },
    {
      title: "Expand assessment coverage",
      detail: "Repeat the assessment with additional prompt variants, target profiles, and representative operational context before making production risk decisions.",
      priority: "Planned",
    },
  ];
}

function executiveNarrative(result: AssessmentResult, findings: ReportFinding[]): string {
  const observed = findings.filter((finding) => finding.status === "observed" && finding.severity !== "informational").length;
  const turns = result.summary.total_turns;
  if (observed > 0) {
    return `The assessment completed ${turns} turn${turns === 1 ? "" : "s"} and identified ${observed} finding${observed === 1 ? "" : "s"} requiring security review. Evidence is derived from the recorded execution transcript and configured heuristic evaluation.`;
  }
  return `The assessment completed ${turns} turn${turns === 1 ? "" : "s"} without a qualifying vulnerability signal. The result should be treated as scoped evidence for this objective, target, and configuration.`;
}

function finding(input: ReportFinding): ReportFinding {
  return input;
}

function metric(label: string, value: string, detail?: string): ReportMetric {
  return { label, value, detail };
}

function severityFromScore(score: number): ReportSeverity {
  if (score >= 0.9) return "critical";
  if (score >= 0.7) return "high";
  if (score >= 0.45) return "medium";
  return "low";
}

function verdictLabel(value: string): string {
  const labels: Record<string, string> = {
    signal_detected: "Security signal detected",
    no_signal: "No qualifying signal",
    inconclusive: "Inconclusive",
    pending: "Pending",
  };
  return labels[value] ?? sentence(value);
}

function sentence(value: string): string {
  return value.replace(/[_-]+/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function shortId(value: string): string {
  return value.slice(0, 8);
}

function truncate(value: string, length: number): string {
  return value.length > length ? `${value.slice(0, length - 1).trim()}...` : value;
}

function unique(values: string[]): string[] {
  return [...new Set(values.filter(Boolean))];
}
