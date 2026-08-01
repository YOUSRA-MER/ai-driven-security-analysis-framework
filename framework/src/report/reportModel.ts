import type { AttackRun, HeuristicEvaluation, RunEvent } from "../types";

export type AssessmentResult = AttackRun;

export type ReportSeverity = "critical" | "high" | "medium" | "low" | "informational";
export type FindingStatus = "observed" | "not_observed" | "inconclusive";

export interface ReportMetric {
  label: string;
  value: string;
  detail?: string;
}

export interface ReportDistributionItem {
  label: string;
  value: number;
  tone: ReportSeverity | "safe" | "warning";
  detail?: string;
}

export interface ReportReference {
  framework: "OWASP" | "MITRE";
  label: string;
  detail?: string;
}

export interface ReportTimelineItem {
  label: string;
  phase: string;
  timestamp: string;
  level: RunEvent["level"];
  detail: string;
}

export interface ReportPromptAnalysis {
  turnNumber: number;
  attackFamily: string;
  strategy: string;
  promptPreview: string;
  responsePreview: string;
  status: string;
  latencyMs: number;
  evaluation?: HeuristicEvaluation;
  evidence: string[];
}

export interface ReportFinding {
  id: string;
  title: string;
  severity: ReportSeverity;
  status: FindingStatus;
  summary: string;
  affectedTurns: number[];
  evidence: string[];
  recommendation: string;
}

export interface AssessmentReport {
  id: string;
  generatedAt: string;
  runId: string;
  title: string;
  executiveSummary: {
    verdict: string;
    narrative: string;
    riskScore: number;
    confidence: number;
    keyMetrics: ReportMetric[];
  };
  targetInformation: ReportMetric[];
  assessmentConfiguration: ReportMetric[];
  timeline: ReportTimelineItem[];
  promptAnalysis: ReportPromptAnalysis[];
  findings: ReportFinding[];
  evidence: Array<{
    id: string;
    title: string;
    detail: string;
    timestamp?: string;
  }>;
  recommendations: Array<{
    title: string;
    detail: string;
    priority: "Immediate" | "Planned" | "Monitor";
    owner: string;
    timeframe: string;
    controlArea: string;
  }>;
  metadata: ReportMetric[];
  visualizations: {
    severityDistribution: ReportDistributionItem[];
    turnDisposition: ReportDistributionItem[];
    confidenceSummary: ReportMetric[];
    latencySummary: ReportMetric[];
  };
  references: {
    owasp: ReportReference[];
    mitre: ReportReference[];
  };
  statistics: ReportMetric[];
}
