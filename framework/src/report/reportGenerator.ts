import type {
  AssessmentReport,
  AssessmentResult,
  ReportDistributionItem,
  ReportFinding,
  ReportMetric,
  ReportPromptAnalysis,
  ReportReference,
  ReportSeverity,
  ReportTimelineItem,
} from "./reportModel";

export function generateAssessmentReport(result: AssessmentResult): AssessmentReport {
  const riskScore = Math.round(Math.min(Math.max(result.summary.maximum_heuristic_score, 0), 1) * 100);
  const confidence = result.planner ? Math.round(result.planner.confidence * 100) : 0;
  const promptAnalysis = buildPromptAnalysis(result);
  const findings = buildFindings(result, promptAnalysis);
  const visualizations = buildVisualizations(result, promptAnalysis, findings, confidence);
  const references = buildReferences(result);

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
    metadata: buildMetadata(result),
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
    visualizations,
    references,
    statistics: [
      metric("Observed findings", String(findings.filter((finding) => finding.status === "observed" && finding.severity !== "informational").length), "Findings requiring analyst review."),
      metric("Safe turns", String(visualizations.turnDisposition.find((item) => item.label === "Safe")?.value ?? 0), "Turns without a vulnerable or suspicious heuristic label."),
      metric("Average latency", averageLatencyLabel(result, promptAnalysis), "Mean response time across attempted turns."),
      metric("Reference mappings", String(references.owasp.length + references.mitre.length), "OWASP and MITRE mappings discovered in assessment metadata."),
    ],
  };
}

function buildMetadata(result: AssessmentResult): ReportMetric[] {
  return [
    metric("Report ID", `report-${shortId(result.run_id)}`),
    metric("Run ID", result.run_id),
    metric("Created", formatDateTime(result.created_at)),
    metric("Updated", formatDateTime(result.updated_at)),
    metric("Plan ID", result.planner?.plan_id || "Not available"),
    metric("Execution ID", result.execution?.execution_id || "Not available"),
    metric("Assessment status", sentence(result.status), result.phase),
    metric("Target", `${result.target.provider} / ${result.target.model}`, result.target.base_url),
  ];
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

function buildVisualizations(
  result: AssessmentResult,
  prompts: ReportPromptAnalysis[],
  findings: ReportFinding[],
  confidence: number,
): AssessmentReport["visualizations"] {
  const severityOrder: ReportSeverity[] = ["critical", "high", "medium", "low", "informational"];
  const severityDistribution = severityOrder.map((severity) => ({
    label: sentence(severity),
    value: findings.filter((finding) => finding.severity === severity).length,
    tone: severity,
    detail: severity === "informational" ? "Contextual observations" : "Security findings",
  }));

  const vulnerable = prompts.filter((prompt) => prompt.evaluation?.label === "vulnerable").length;
  const suspicious = prompts.filter((prompt) => prompt.evaluation?.label === "suspicious").length;
  const inconclusive = prompts.filter((prompt) => prompt.evaluation?.label === "inconclusive").length;
  const attempted = prompts.length || result.summary.total_turns;
  const failed = Math.max(result.summary.failed_turns, prompts.filter((prompt) => prompt.status === "error").length);
  const safe = Math.max(0, attempted - vulnerable - suspicious - inconclusive - failed);
  const turnDisposition: ReportDistributionItem[] = [
    { label: "Vulnerable", value: vulnerable, tone: "critical", detail: "Turns with vulnerable heuristic labels" },
    { label: "Suspicious", value: suspicious, tone: "warning", detail: "Turns requiring review" },
    { label: "Inconclusive", value: inconclusive, tone: "informational", detail: "Insufficient signal" },
    { label: "Safe", value: safe, tone: "safe", detail: "No qualifying signal" },
    { label: "Failed", value: failed, tone: "low", detail: "Execution errors or failed turns" },
  ];

  const promptConfidences = (result.planner?.generated_prompts ?? [])
    .map((prompt) => prompt.confidence)
    .filter((value): value is number => typeof value === "number" && Number.isFinite(value));
  const averagePromptConfidence = promptConfidences.length
    ? Math.round(promptConfidences.reduce((sum, value) => sum + value, 0) / promptConfidences.length * 100)
    : confidence;

  const confidenceSummary = [
    metric("Planner confidence", `${confidence}%`, result.planner?.confidence_level ? sentence(result.planner.confidence_level) : "Planner confidence level"),
    metric("Prompt confidence", `${averagePromptConfidence}%`, `${promptConfidences.length} generated prompt confidence value${promptConfidences.length === 1 ? "" : "s"}`),
    metric("Heuristic confidence", `${Math.round(result.summary.maximum_heuristic_score * 100)}%`, "Maximum observed heuristic score"),
    metric("Decision quality", result.summary.heuristic_label === "inconclusive" ? "Review required" : "Decision-ready", verdictLabel(result.summary.heuristic_label)),
  ];

  const latencies = prompts.map((prompt) => prompt.latencyMs).filter((value) => Number.isFinite(value) && value > 0);
  const metrics = result.execution?.execution_metrics;
  const average = metrics?.average_latency_ms || averageValue(latencies);
  const minimum = metrics?.minimum_latency_ms || (latencies.length ? Math.min(...latencies) : 0);
  const maximum = metrics?.maximum_latency_ms || Math.max(...latencies, 0);
  const total = result.summary.total_latency_ms || result.execution?.total_latency || latencies.reduce((sum, value) => sum + value, 0);
  const latencySummary = [
    metric("Average latency", formatDuration(average), "Mean turn response time"),
    metric("Minimum latency", formatDuration(minimum), "Fastest successful turn"),
    metric("Maximum latency", formatDuration(maximum), "Slowest successful turn"),
    metric("Total latency", formatDuration(total), "Aggregate assessment response time"),
  ];

  return { severityDistribution, turnDisposition, confidenceSummary, latencySummary };
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
      owner: "Security engineering",
      timeframe: hasObservedFinding ? "24-48 hours" : "Next regression cycle",
      controlArea: "Detection and validation",
    },
    {
      title: "Harden the tested control boundary",
      detail: `Focus remediation on ${attackFamily || "the selected attack family"} using the generated prompts, transcript, and heuristic evidence in this report.`,
      priority: hasObservedFinding ? "Immediate" : "Planned",
      owner: "Application owner",
      timeframe: hasObservedFinding ? "Current sprint" : "Planned hardening window",
      controlArea: "Prompt and context controls",
    },
    {
      title: "Expand assessment coverage",
      detail: "Repeat the assessment with additional prompt variants, target profiles, and representative operational context before making production risk decisions.",
      priority: "Planned",
      owner: "AI risk program",
      timeframe: "Next assessment cycle",
      controlArea: "Continuous assurance",
    },
  ];
}

function buildReferences(result: AssessmentResult): AssessmentReport["references"] {
  const values = collectReferenceValues(result);
  return {
    owasp: uniqueReferences(values
      .filter((item) => /owasp|llm\d\d?/i.test(item))
      .flatMap((item) => splitReferenceValue(item, "OWASP"))),
    mitre: uniqueReferences(values
      .filter((item) => /mitre|atlas|aml\.t/i.test(item))
      .flatMap((item) => splitReferenceValue(item, "MITRE"))),
  };
}

function collectReferenceValues(result: AssessmentResult): string[] {
  const values: string[] = [];
  const visit = (value: unknown, key = "") => {
    if (value == null) return;
    if (typeof value === "string" || typeof value === "number") {
      const text = String(value).trim();
      if (text && /owasp|mitre|atlas|aml\.t|llm\d\d?/i.test(`${key} ${text}`)) values.push(text);
      return;
    }
    if (Array.isArray(value)) {
      value.forEach((item) => visit(item, key));
      return;
    }
    if (typeof value === "object") {
      Object.entries(value as Record<string, unknown>).forEach(([nextKey, nextValue]) => visit(nextValue, nextKey));
    }
  };

  visit(result.planner?.generated_prompts);
  visit(result.planner?.steps);
  visit(result.execution?.metadata);
  visit(result.execution?.conversation_history.map((turn) => turn.metadata));
  visit(result.events?.map((event) => event.data));
  return unique(values);
}

function splitReferenceValue(value: string, framework: ReportReference["framework"]): ReportReference[] {
  return value
    .split(/[;,|]/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => ({
      framework,
      label: normalizeReferenceLabel(item, framework),
      detail: item,
    }))
    .filter((item, index, all) => all.findIndex((candidate) => candidate.label === item.label) === index);
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

function formatDateTime(value: string): string {
  const timestamp = Date.parse(value);
  if (Number.isNaN(timestamp)) return value;
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(timestamp);
}

function formatDuration(milliseconds: number): string {
  if (!Number.isFinite(milliseconds) || milliseconds <= 0) return "0 ms";
  if (milliseconds < 1000) return `${Math.round(milliseconds)} ms`;
  if (milliseconds < 60000) return `${(milliseconds / 1000).toFixed(1)} s`;
  return `${Math.floor(milliseconds / 60000)}m ${Math.round((milliseconds % 60000) / 1000)}s`;
}

function averageLatencyLabel(result: AssessmentResult, prompts: ReportPromptAnalysis[]): string {
  const average = result.execution?.execution_metrics.average_latency_ms || averageValue(prompts.map((prompt) => prompt.latencyMs));
  return formatDuration(average);
}

function averageValue(values: number[]): number {
  const valid = values.filter((value) => Number.isFinite(value) && value > 0);
  if (valid.length === 0) return 0;
  return valid.reduce((sum, value) => sum + value, 0) / valid.length;
}

function normalizeReferenceLabel(value: string, framework: ReportReference["framework"]): string {
  const owasp = value.match(/LLM\d\d?(?::?2025)?(?:\s*[-:]\s*[^;|,]+)?/i);
  if (framework === "OWASP" && owasp) return owasp[0].replace(/\s+/g, " ").trim();
  const mitre = value.match(/AML\.T\d+(?:[-.]\d+)?(?:\s*[-:]\s*[^;|,]+)?/i);
  if (framework === "MITRE" && mitre) return mitre[0].replace(/\s+/g, " ").trim();
  return value.replace(/\s+/g, " ").trim();
}

function uniqueReferences(references: ReportReference[]): ReportReference[] {
  return references.filter((reference, index, all) => all.findIndex((candidate) => candidate.label === reference.label) === index);
}

function truncate(value: string, length: number): string {
  return value.length > length ? `${value.slice(0, length - 1).trim()}...` : value;
}

function unique(values: string[]): string[] {
  return [...new Set(values.filter(Boolean))];
}
