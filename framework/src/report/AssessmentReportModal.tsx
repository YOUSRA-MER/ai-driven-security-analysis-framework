import { AlertTriangle, BarChart3, CheckCircle2, Clock3, FileText, Gauge, ListChecks, ShieldAlert, Target } from "lucide-react";
import { useMemo } from "react";
import type { ReactNode } from "react";
import { Badge, Button, Modal } from "../components/ui";
import { generateAssessmentReport } from "./reportGenerator";
import type { AssessmentResult, ReportFinding, ReportMetric, ReportSeverity } from "./reportModel";

export function AssessmentReportModal({
  open,
  result,
  onClose,
}: {
  open: boolean;
  result: AssessmentResult | null;
  onClose: () => void;
}) {
  const report = useMemo(() => (result ? generateAssessmentReport(result) : null), [result]);
  if (!report) return null;

  return (
    <Modal
      className="assessment-report-modal"
      description={`Generated ${formatDateTime(report.generatedAt)} from existing assessment result data.`}
      onClose={onClose}
      open={open}
      size="lg"
      title="Assessment Report"
      footer={<Button variant="primary" onClick={onClose}>Close report</Button>}
    >
      <article className="assessment-report" aria-labelledby="assessment-report-title">
        <header className="report-cover">
          <div>
            <span className="eyebrow">Devoteam RedLens</span>
            <h2 id="assessment-report-title">{report.title}</h2>
            <p>{report.executiveSummary.narrative}</p>
          </div>
          <div className="report-verdict">
            <Badge tone={report.executiveSummary.riskScore > 69 ? "danger" : report.executiveSummary.riskScore > 39 ? "warning" : "success"} rounded>
              {report.executiveSummary.verdict}
            </Badge>
            <strong>{report.executiveSummary.riskScore}<small>/100</small></strong>
            <span>Risk score</span>
          </div>
        </header>

        <ReportSection title="Executive Summary" icon={<Gauge size={18} />}>
          <MetricGrid metrics={report.executiveSummary.keyMetrics} />
        </ReportSection>

        <div className="report-two-column">
          <ReportSection title="Target Information" icon={<Target size={18} />}>
            <DefinitionList metrics={report.targetInformation} />
          </ReportSection>
          <ReportSection title="Assessment Configuration" icon={<ListChecks size={18} />}>
            <DefinitionList metrics={report.assessmentConfiguration} />
          </ReportSection>
        </div>

        <ReportSection title="Timeline" icon={<Clock3 size={18} />}>
          <ol className="report-timeline">
            {report.timeline.map((item, index) => (
              <li className={`level-${item.level}`} key={`${item.timestamp}-${index}`}>
                <time dateTime={item.timestamp}>{formatDateTime(item.timestamp)}</time>
                <div><strong>{item.label}</strong><span>{item.phase} - {item.detail}</span></div>
              </li>
            ))}
          </ol>
        </ReportSection>

        <ReportSection title="Prompt Analysis" icon={<FileText size={18} />}>
          <div className="report-prompt-analysis">
            {report.promptAnalysis.map((item) => (
              <details key={item.turnNumber} open={item.turnNumber === 1}>
                <summary>
                  <span>Turn {item.turnNumber}</span>
                  <strong>{item.attackFamily || "Attack prompt"}</strong>
                  <Badge tone={item.evaluation?.label === "vulnerable" ? "danger" : item.evaluation?.label === "suspicious" ? "warning" : "neutral"} size="sm">
                    {item.evaluation?.label ?? item.status}
                  </Badge>
                </summary>
                <div className="report-prompt-body">
                  <EvidenceBlock title="Prompt" value={item.promptPreview} />
                  <EvidenceBlock title="Response" value={item.responsePreview} />
                  <DefinitionList
                    metrics={[
                      { label: "Strategy", value: item.strategy || "Unspecified" },
                      { label: "Latency", value: formatDuration(item.latencyMs) },
                      { label: "Evidence", value: item.evidence.length ? item.evidence.join(", ") : "None recorded" },
                    ]}
                  />
                </div>
              </details>
            ))}
            {report.promptAnalysis.length === 0 && <p className="report-empty">No execution transcript is available for this assessment.</p>}
          </div>
        </ReportSection>

        <ReportSection title="Findings" icon={<ShieldAlert size={18} />}>
          <div className="report-findings">
            {report.findings.map((finding) => <FindingCard finding={finding} key={finding.id} />)}
          </div>
        </ReportSection>

        <ReportSection title="Evidence" icon={<FileText size={18} />}>
          <div className="report-evidence-list">
            {report.evidence.map((item) => (
              <EvidenceBlock key={item.id} title={item.title} value={item.detail} />
            ))}
            {report.evidence.length === 0 && <p className="report-empty">No evidence items were collected.</p>}
          </div>
        </ReportSection>

        <ReportSection title="Recommendations" icon={<CheckCircle2 size={18} />}>
          <div className="report-recommendations">
            {report.recommendations.map((item) => (
              <article key={item.title}>
                <Badge tone={item.priority === "Immediate" ? "danger" : item.priority === "Planned" ? "info" : "neutral"} size="sm">{item.priority}</Badge>
                <div><strong>{item.title}</strong><p>{item.detail}</p></div>
              </article>
            ))}
          </div>
        </ReportSection>

        <ReportSection title="Statistics" icon={<BarChart3 size={18} />}>
          <MetricGrid metrics={report.statistics} />
        </ReportSection>
      </article>
    </Modal>
  );
}

function ReportSection({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) {
  return (
    <section className="report-section" aria-labelledby={`report-${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}>
      <h3 id={`report-${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}>{icon}{title}</h3>
      {children}
    </section>
  );
}

function MetricGrid({ metrics }: { metrics: ReportMetric[] }) {
  return (
    <div className="report-metric-grid">
      {metrics.map((metric) => (
        <div key={metric.label}>
          <span>{metric.label}</span>
          <strong>{metric.value}</strong>
          {metric.detail && <small>{metric.detail}</small>}
        </div>
      ))}
    </div>
  );
}

function DefinitionList({ metrics }: { metrics: ReportMetric[] }) {
  return (
    <dl className="report-definition-list">
      {metrics.map((metric) => (
        <div key={metric.label}>
          <dt>{metric.label}</dt>
          <dd>{metric.value}</dd>
          {metric.detail && <small>{metric.detail}</small>}
        </div>
      ))}
    </dl>
  );
}

function FindingCard({ finding }: { finding: ReportFinding }) {
  return (
    <article className={`report-finding severity-${finding.severity}`}>
      <div className="report-finding-heading">
        <span>{finding.status === "observed" ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}</span>
        <div><strong>{finding.title}</strong><small>{finding.affectedTurns.length ? `Turns ${finding.affectedTurns.join(", ")}` : "Assessment level"}</small></div>
        <Badge tone={severityTone(finding.severity)} size="sm">{finding.severity}</Badge>
      </div>
      <p>{finding.summary}</p>
      {finding.evidence.length > 0 && <ul>{finding.evidence.map((item) => <li key={item}>{item}</li>)}</ul>}
      <div className="report-finding-recommendation"><strong>Recommendation</strong><span>{finding.recommendation}</span></div>
    </article>
  );
}

function EvidenceBlock({ title, value }: { title: string; value: string }) {
  return (
    <section className="report-evidence-block">
      <h4>{title}</h4>
      <pre>{value || "No content recorded."}</pre>
    </section>
  );
}

function severityTone(severity: ReportSeverity) {
  if (severity === "critical" || severity === "high") return "danger";
  if (severity === "medium") return "warning";
  if (severity === "low") return "info";
  return "neutral";
}

function formatDateTime(value: string): string {
  const timestamp = Date.parse(value);
  if (Number.isNaN(timestamp)) return value;
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(timestamp);
}

function formatDuration(milliseconds: number): string {
  if (!Number.isFinite(milliseconds) || milliseconds <= 0) return "0 ms";
  if (milliseconds < 1000) return `${Math.round(milliseconds)} ms`;
  return `${(milliseconds / 1000).toFixed(1)} s`;
}
