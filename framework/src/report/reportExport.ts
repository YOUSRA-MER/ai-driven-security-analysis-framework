import type { AssessmentReport, ReportDistributionItem, ReportMetric, ReportReference } from "./reportModel";

type PdfFont = "regular" | "bold" | "mono";
type PdfColor = [number, number, number];

interface PdfPage {
  commands: string[];
  cover: boolean;
}

const PAGE_WIDTH = 612;
const PAGE_HEIGHT = 792;
const MARGIN = 54;
const CONTENT_TOP = 706;
const CONTENT_BOTTOM = 66;
const CONTENT_WIDTH = PAGE_WIDTH - MARGIN * 2;

const COLOR_TEXT: PdfColor = [0.11, 0.13, 0.17];
const COLOR_MUTED: PdfColor = [0.39, 0.44, 0.52];
const COLOR_BORDER: PdfColor = [0.82, 0.85, 0.9];
const COLOR_SURFACE: PdfColor = [0.96, 0.97, 0.98];
const COLOR_BRAND: PdfColor = [0.78, 0.05, 0.16];
const COLOR_NAVY: PdfColor = [0.08, 0.13, 0.19];
const COLOR_WHITE: PdfColor = [1, 1, 1];

export function downloadReportHtml(report: AssessmentReport): void {
  downloadBlob(renderStandaloneHtml(report), htmlFilename(report), "text/html;charset=utf-8");
}

export function downloadReportPdf(report: AssessmentReport): void {
  downloadBlob(renderPdf(report), pdfFilename(report), "application/pdf");
}

function renderPdf(report: AssessmentReport): string {
  const pages: PdfPage[] = [];
  let currentPage: PdfPage = { commands: [], cover: false };
  let y = CONTENT_TOP;

  const addPage = (cover = false) => {
    currentPage = { commands: [], cover };
    pages.push(currentPage);
    y = CONTENT_TOP;
    return currentPage;
  };

  const ensureSpace = (height: number) => {
    if (y - height < CONTENT_BOTTOM) addPage();
  };

  const drawText = (
    text: string,
    x: number,
    lineY: number,
    size: number,
    font: PdfFont = "regular",
    color: PdfColor = COLOR_TEXT,
  ) => {
    currentPage.commands.push(`BT /${fontRef(font)} ${size} Tf ${rgb(color)} ${fixed(x)} ${fixed(lineY)} Td ${pdfText(text)} Tj ET`);
  };

  const writeLines = (
    text: string,
    x: number,
    width: number,
    size = 9,
    lineHeight = 13,
    font: PdfFont = "regular",
    color: PdfColor = COLOR_TEXT,
  ) => {
    for (const line of wrapText(text, width, size)) {
      ensureSpace(lineHeight);
      drawText(line, x, y, size, font, color);
      y -= lineHeight;
    }
  };

  const addSection = (title: string) => {
    ensureSpace(42);
    currentPage.commands.push(`${rgb(COLOR_BRAND)} ${fixed(MARGIN)} ${fixed(y - 4)} 4 18 re f`);
    drawText(title.toUpperCase(), MARGIN + 12, y, 12, "bold", COLOR_TEXT);
    y -= 28;
  };

  const addMetricCards = (metrics: ReportMetric[]) => {
    const gap = 12;
    const cardWidth = (CONTENT_WIDTH - gap) / 2;
    for (let index = 0; index < metrics.length; index += 2) {
      const pair = metrics.slice(index, index + 2);
      const heights = pair.map((metric) => {
        const valueLines = wrapText(metric.value, cardWidth - 24, 10);
        const detailLines = metric.detail ? wrapText(metric.detail, cardWidth - 24, 8) : [];
        return Math.max(62, 28 + valueLines.length * 12 + detailLines.length * 10);
      });
      const cardHeight = Math.max(...heights);
      ensureSpace(cardHeight + 10);
      pair.forEach((metric, pairIndex) => {
        const x = MARGIN + pairIndex * (cardWidth + gap);
        drawBox(currentPage, x, y - cardHeight + 8, cardWidth, cardHeight, COLOR_SURFACE);
        drawText(metric.label.toUpperCase(), x + 12, y - 10, 7, "bold", COLOR_MUTED);
        let textY = y - 26;
        for (const line of wrapText(metric.value, cardWidth - 24, 10).slice(0, 5)) {
          drawText(line, x + 12, textY, 10, "bold", COLOR_TEXT);
          textY -= 12;
        }
        if (metric.detail) {
          for (const line of wrapText(metric.detail, cardWidth - 24, 8).slice(0, 4)) {
            drawText(line, x + 12, textY - 1, 8, "regular", COLOR_MUTED);
            textY -= 10;
          }
        }
      });
      y -= cardHeight + 10;
    }
  };

  const addDefinitionTable = (metrics: ReportMetric[]) => {
    for (const metric of metrics) {
      const lines = wrapText(metric.value, CONTENT_WIDTH - 150, 9);
      const detailLines = metric.detail ? wrapText(metric.detail, CONTENT_WIDTH - 150, 8) : [];
      const rowHeight = Math.max(24, 12 + lines.length * 11 + detailLines.length * 9);
      ensureSpace(rowHeight);
      drawText(metric.label, MARGIN, y, 8, "bold", COLOR_MUTED);
      let textY = y;
      for (const line of lines) {
        drawText(line, MARGIN + 150, textY, 9, "regular", COLOR_TEXT);
        textY -= 11;
      }
      for (const line of detailLines) {
        drawText(line, MARGIN + 150, textY, 8, "regular", COLOR_MUTED);
        textY -= 9;
      }
      currentPage.commands.push(`${rgb(COLOR_BORDER)} ${fixed(MARGIN)} ${fixed(y - rowHeight + 8)} ${fixed(CONTENT_WIDTH)} 0.6 re f`);
      y -= rowHeight;
    }
    y -= 8;
  };

  const addParagraphBlock = (title: string, body: string, accent: PdfColor = COLOR_BORDER) => {
    const titleLines = wrapText(title, CONTENT_WIDTH - 24, 10);
    const bodyLines = wrapText(body || "No content recorded.", CONTENT_WIDTH - 24, 8.5);
    const height = 28 + titleLines.length * 12 + bodyLines.length * 11;
    ensureSpace(Math.min(height, PAGE_HEIGHT - 150));
    currentPage.commands.push(`${rgb(accent)} ${fixed(MARGIN)} ${fixed(y - 2)} 3 ${fixed(Math.min(height - 8, y - CONTENT_BOTTOM))} re f`);
    for (const line of titleLines) {
      drawText(line, MARGIN + 12, y, 10, "bold", COLOR_TEXT);
      y -= 12;
    }
    y -= 4;
    for (const line of bodyLines) {
      ensureSpace(11);
      drawText(line, MARGIN + 12, y, 8.5, "regular", COLOR_TEXT);
      y -= 11;
    }
    y -= 10;
  };

  addPage(true);
  drawCover(currentPage, report);
  addPage();

  addSection("Executive Summary");
  writeLines(report.executiveSummary.narrative, MARGIN, CONTENT_WIDTH, 10, 14);
  y -= 6;
  addMetricCards(report.executiveSummary.keyMetrics);

  addSection("Assessment Metadata");
  addMetricCards(report.metadata);

  addSection("Security Analytics");
  addParagraphBlock("Severity Distribution", report.visualizations.severityDistribution.map((item) => `${item.label}: ${item.value}`).join("\n"));
  addParagraphBlock("Vulnerable vs Safe Turns", report.visualizations.turnDisposition.map((item) => `${item.label}: ${item.value}`).join("\n"));
  addMetricCards(report.visualizations.confidenceSummary);
  addMetricCards(report.visualizations.latencySummary);

  addSection("Target Information");
  addDefinitionTable(report.targetInformation);

  addSection("Assessment Configuration");
  addDefinitionTable(report.assessmentConfiguration);

  addSection("Timeline");
  report.timeline.forEach((item) => {
    addParagraphBlock(`${formatDateTime(item.timestamp)} | ${item.phase}`, `${item.label}\n${item.detail}`);
  });

  addSection("Prompt Analysis");
  if (report.promptAnalysis.length === 0) {
    writeLines("No execution transcript is available for this assessment.", MARGIN, CONTENT_WIDTH, 9, 13, "regular", COLOR_MUTED);
  }
  report.promptAnalysis.forEach((item) => {
    addParagraphBlock(
      `Turn ${item.turnNumber} | ${item.attackFamily || "Attack prompt"} | ${item.evaluation?.label ?? item.status}`,
      [
        `Strategy: ${item.strategy || "Unspecified"}`,
        `Latency: ${formatDuration(item.latencyMs)}`,
        `Prompt: ${item.promptPreview}`,
        `Response: ${item.responsePreview}`,
        `Evidence: ${item.evidence.length ? item.evidence.join(", ") : "None recorded"}`,
      ].join("\n"),
      item.evaluation?.label === "vulnerable" ? COLOR_BRAND : COLOR_BORDER,
    );
  });

  addSection("Findings");
  report.findings.forEach((finding) => {
    addParagraphBlock(
      `${finding.severity.toUpperCase()} | ${finding.title}`,
      [
        finding.summary,
        finding.affectedTurns.length ? `Affected turns: ${finding.affectedTurns.join(", ")}` : "Assessment level finding.",
        finding.evidence.length ? `Evidence: ${finding.evidence.join("; ")}` : "",
        `Recommendation: ${finding.recommendation}`,
      ].filter(Boolean).join("\n"),
      finding.severity === "critical" || finding.severity === "high" ? COLOR_BRAND : COLOR_BORDER,
    );
  });

  addSection("Evidence");
  if (report.evidence.length === 0) writeLines("No evidence items were collected.", MARGIN, CONTENT_WIDTH, 9, 13, "regular", COLOR_MUTED);
  report.evidence.forEach((item) => addParagraphBlock(item.title, item.detail));

  addSection("Recommendations");
  report.recommendations.forEach((item) => addParagraphBlock(
    `${item.priority} | ${item.title}`,
    `${item.detail}\nOwner: ${item.owner}\nTimeframe: ${item.timeframe}\nControl area: ${item.controlArea}`,
  ));

  if (report.references.owasp.length > 0 || report.references.mitre.length > 0) {
    addSection("Framework References");
    if (report.references.owasp.length > 0) addParagraphBlock("OWASP LLM Top 10", report.references.owasp.map((item) => `${item.label}${item.detail && item.detail !== item.label ? ` - ${item.detail}` : ""}`).join("\n"));
    if (report.references.mitre.length > 0) addParagraphBlock("MITRE ATLAS", report.references.mitre.map((item) => `${item.label}${item.detail && item.detail !== item.label ? ` - ${item.detail}` : ""}`).join("\n"));
  }

  addSection("Statistics");
  addMetricCards(report.statistics);

  return buildPdfDocument(pages, report);
}

function drawCover(page: PdfPage, report: AssessmentReport): void {
  page.commands.push(`${rgb(COLOR_NAVY)} 0 0 ${PAGE_WIDTH} ${PAGE_HEIGHT} re f`);
  page.commands.push(`${rgb(COLOR_BRAND)} 0 0 12 ${PAGE_HEIGHT} re f`);
  page.commands.push(`${rgb([0.12, 0.18, 0.26])} ${MARGIN} 120 ${PAGE_WIDTH - MARGIN * 2} 540 re f`);
  page.commands.push(`BT /F2 11 Tf ${rgb(COLOR_WHITE)} ${MARGIN + 28} 616 Td ${pdfText("DEVOTEAM REDLENS")} Tj ET`);
  page.commands.push(`BT /F2 28 Tf ${rgb(COLOR_WHITE)} ${MARGIN + 28} 566 Td ${pdfText(report.title)} Tj ET`);
  page.commands.push(`BT /F1 11 Tf ${rgb([0.82, 0.87, 0.93])} ${MARGIN + 28} 532 Td ${pdfText(`Generated ${formatDateTime(report.generatedAt)}`)} Tj ET`);
  page.commands.push(`BT /F1 10 Tf ${rgb([0.82, 0.87, 0.93])} ${MARGIN + 28} 504 Td ${pdfText(`Run ID ${report.runId}`)} Tj ET`);
  for (const [index, line] of wrapText(report.executiveSummary.narrative, 410, 12).slice(0, 7).entries()) {
    page.commands.push(`BT /F1 12 Tf ${rgb(COLOR_WHITE)} ${MARGIN + 28} ${454 - index * 17} Td ${pdfText(line)} Tj ET`);
  }
  page.commands.push(`${rgb(COLOR_WHITE)} ${PAGE_WIDTH - 220} 272 120 120 re f`);
  page.commands.push(`BT /F2 32 Tf ${rgb(COLOR_NAVY)} ${PAGE_WIDTH - 192} 336 Td ${pdfText(String(report.executiveSummary.riskScore))} Tj ET`);
  page.commands.push(`BT /F1 10 Tf ${rgb(COLOR_MUTED)} ${PAGE_WIDTH - 181} 314 Td ${pdfText("Risk score")} Tj ET`);
  page.commands.push(`BT /F2 12 Tf ${rgb(COLOR_WHITE)} ${MARGIN + 28} 196 Td ${pdfText(report.executiveSummary.verdict)} Tj ET`);
}

function buildPdfDocument(pages: PdfPage[], report: AssessmentReport): string {
  const objects: string[] = [];
  const pageRefs: number[] = [];
  objects.push("<< /Type /Catalog /Pages 2 0 R >>");
  objects.push("");
  objects.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>");
  objects.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>");
  objects.push("<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>");

  pages.forEach((page, index) => {
    const pageNumber = objects.length + 1;
    const contentNumber = objects.length + 2;
    pageRefs.push(pageNumber);
    const stream = [...page.commands, ...renderPageChrome(page, report, index + 1, pages.length)].join("\n");
    objects.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${PAGE_WIDTH} ${PAGE_HEIGHT}] /Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> /Contents ${contentNumber} 0 R >>`);
    objects.push(`<< /Length ${byteLength(stream)} >>\nstream\n${stream}\nendstream`);
  });

  objects[1] = `<< /Type /Pages /Kids [${pageRefs.map((ref) => `${ref} 0 R`).join(" ")}] /Count ${pages.length} >>`;

  const chunks = ["%PDF-1.4\n"];
  const offsets = [0];
  let offset = byteLength(chunks[0]);
  objects.forEach((object, index) => {
    offsets[index + 1] = offset;
    const chunk = `${index + 1} 0 obj\n${object}\nendobj\n`;
    chunks.push(chunk);
    offset += byteLength(chunk);
  });
  const xrefOffset = offset;
  const xref = [
    `xref\n0 ${objects.length + 1}`,
    "0000000000 65535 f ",
    ...offsets.slice(1).map((item) => `${String(item).padStart(10, "0")} 00000 n `),
    `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>`,
    `startxref\n${xrefOffset}`,
    "%%EOF",
  ].join("\n");
  chunks.push(xref);
  return chunks.join("");
}

function renderPageChrome(page: PdfPage, report: AssessmentReport, pageNumber: number, pageCount: number): string[] {
  const commands: string[] = [];
  if (!page.cover) {
    commands.push(`${rgb(COLOR_BORDER)} ${MARGIN} 736 ${CONTENT_WIDTH} 0.7 re f`);
    commands.push(`BT /F2 8 Tf ${rgb(COLOR_MUTED)} ${MARGIN} 754 Td ${pdfText("Devoteam RedLens Assessment Report")} Tj ET`);
    commands.push(`BT /F1 8 Tf ${rgb(COLOR_MUTED)} ${MARGIN} 740 Td ${pdfText(report.runId)} Tj ET`);
  }
  commands.push(`${rgb(COLOR_BORDER)} ${MARGIN} 48 ${CONTENT_WIDTH} 0.7 re f`);
  commands.push(`BT /F1 8 Tf ${rgb(COLOR_MUTED)} ${MARGIN} 32 Td ${pdfText(formatDateTime(report.generatedAt))} Tj ET`);
  commands.push(`BT /F1 8 Tf ${rgb(COLOR_MUTED)} ${PAGE_WIDTH - MARGIN - 70} 32 Td ${pdfText(`Page ${pageNumber} of ${pageCount}`)} Tj ET`);
  return commands;
}

function renderStandaloneHtml(report: AssessmentReport): string {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(report.title)}</title>
  <style>
    :root { color-scheme: light dark; --brand: #c70d2c; --ink: #151922; --muted: #667085; --line: #d9dee7; --surface: #ffffff; --canvas: #f5f7fa; }
    @media (prefers-color-scheme: dark) { :root { --ink: #f3f6fa; --muted: #a8b2c1; --line: #374151; --surface: #101820; --canvas: #0b1118; } }
    * { box-sizing: border-box; }
    body { margin: 0; color: var(--ink); font: 14px/1.55 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--canvas); }
    main { width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0; }
    .cover, section { margin-bottom: 18px; padding: 24px; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; break-inside: avoid; }
    .cover { display: grid; grid-template-columns: minmax(0, 1fr) 180px; gap: 24px; border-top: 6px solid var(--brand); }
    .eyebrow, dt, .metric span { color: var(--muted); font-size: 11px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; }
    h1, h2, h3, p, dl { margin-top: 0; }
    h1 { margin-bottom: 10px; font-size: clamp(28px, 5vw, 44px); line-height: 1.05; }
    h2 { margin-bottom: 16px; font-size: 18px; text-transform: uppercase; }
    h3 { margin: 18px 0 8px; font-size: 15px; }
    .risk { display: grid; align-content: center; padding: 18px; background: color-mix(in srgb, var(--brand) 9%, var(--surface)); border: 1px solid var(--line); border-radius: 6px; }
    .risk strong { display: block; font-size: 40px; line-height: 1; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
    .metric { min-width: 0; padding: 14px; background: var(--canvas); border: 1px solid var(--line); border-radius: 6px; }
    .metric strong, dd { display: block; margin: 4px 0 0; overflow-wrap: anywhere; }
    .metric small, dd small { display: block; margin-top: 4px; color: var(--muted); }
    .analytics { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
    .chart { padding: 14px; background: var(--canvas); border: 1px solid var(--line); border-radius: 6px; }
    .chart h3 { margin-top: 0; }
    .bar { display: grid; gap: 6px; margin-top: 10px; }
    .bar div { height: 9px; overflow: hidden; background: color-mix(in srgb, var(--line) 76%, transparent); border-radius: 999px; }
    .bar span { display: block; width: var(--value); height: 100%; background: var(--brand); border-radius: inherit; }
    dl { display: grid; gap: 10px; }
    dl div { padding-bottom: 10px; border-bottom: 1px solid var(--line); }
    dd { margin-left: 0; }
    .item { padding: 14px 0; border-top: 1px solid var(--line); break-inside: avoid; }
    .item:first-child { border-top: 0; }
    pre { overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; padding: 14px; background: var(--canvas); border: 1px solid var(--line); border-radius: 6px; font: 12px/1.55 ui-monospace, SFMono-Regular, Consolas, monospace; }
    .badge { display: inline-block; margin-bottom: 8px; padding: 3px 8px; color: #fff; background: var(--brand); border-radius: 999px; font-size: 11px; font-weight: 800; text-transform: uppercase; }
    @media (max-width: 760px) { main { width: min(100% - 20px, 1120px); padding: 16px 0; } .cover, .grid, .analytics { grid-template-columns: 1fr; } }
    @media print { :root { --ink: #151922; --muted: #667085; --line: #d9dee7; --surface: #ffffff; --canvas: #ffffff; } body { background: #fff; } main { width: auto; padding: 0; } .cover { min-height: 70vh; page-break-after: always; } section { page-break-inside: avoid; border-radius: 0; } pre { max-height: none; } @page { margin: 16mm; } }
  </style>
</head>
<body>
  <main>
    <article>
      <header class="cover">
        <div>
          <span class="eyebrow">Devoteam RedLens</span>
          <h1>${escapeHtml(report.title)}</h1>
          <p>${escapeHtml(report.executiveSummary.narrative)}</p>
          <p><strong>${escapeHtml(report.executiveSummary.verdict)}</strong> | Generated ${escapeHtml(formatDateTime(report.generatedAt))}</p>
        </div>
        <aside class="risk"><span class="eyebrow">Risk score</span><strong>${report.executiveSummary.riskScore}<small>/100</small></strong><span>${escapeHtml(report.runId)}</span></aside>
      </header>
      ${htmlSection("Executive Summary", htmlMetricGrid(report.executiveSummary.keyMetrics))}
      ${htmlSection("Assessment Metadata", htmlMetricGrid(report.metadata))}
      ${htmlSection("Security Analytics", `<div class="analytics">${htmlDistribution("Severity Distribution", report.visualizations.severityDistribution)}${htmlDistribution("Vulnerable vs Safe Turns", report.visualizations.turnDisposition)}<div class="chart">${htmlMetricGrid(report.visualizations.confidenceSummary)}</div><div class="chart">${htmlMetricGrid(report.visualizations.latencySummary)}</div></div>`)}
      ${htmlSection("Target Information", htmlDefinitionList(report.targetInformation))}
      ${htmlSection("Assessment Configuration", htmlDefinitionList(report.assessmentConfiguration))}
      ${htmlSection("Timeline", report.timeline.map((item) => htmlItem(`${formatDateTime(item.timestamp)} | ${item.phase}`, `${item.label}\n${item.detail}`)).join(""))}
      ${htmlSection("Prompt Analysis", report.promptAnalysis.length ? report.promptAnalysis.map((item) => htmlItem(`Turn ${item.turnNumber} | ${item.attackFamily || "Attack prompt"} | ${item.evaluation?.label ?? item.status}`, `Strategy: ${item.strategy || "Unspecified"}\nLatency: ${formatDuration(item.latencyMs)}\nPrompt: ${item.promptPreview}\n\nResponse: ${item.responsePreview}\n\nEvidence: ${item.evidence.length ? item.evidence.join(", ") : "None recorded"}`)).join("") : "<p>No execution transcript is available for this assessment.</p>")}
      ${htmlSection("Findings", report.findings.map((finding) => htmlItem(`${finding.severity.toUpperCase()} | ${finding.title}`, `${finding.summary}\n${finding.affectedTurns.length ? `Affected turns: ${finding.affectedTurns.join(", ")}` : "Assessment level"}\n${finding.evidence.length ? `Evidence: ${finding.evidence.join("; ")}` : ""}\nRecommendation: ${finding.recommendation}`)).join(""))}
      ${htmlSection("Evidence", report.evidence.length ? report.evidence.map((item) => htmlItem(item.title, item.detail)).join("") : "<p>No evidence items were collected.</p>")}
      ${htmlSection("Recommendations", report.recommendations.map((item) => htmlItem(`${item.priority} | ${item.title}`, `${item.detail}\nOwner: ${item.owner}\nTimeframe: ${item.timeframe}\nControl area: ${item.controlArea}`)).join(""))}
      ${(report.references.owasp.length > 0 || report.references.mitre.length > 0) ? htmlSection("Framework References", `${htmlReferenceList("OWASP LLM Top 10", report.references.owasp)}${htmlReferenceList("MITRE ATLAS", report.references.mitre)}`) : ""}
      ${htmlSection("Statistics", htmlMetricGrid(report.statistics))}
    </article>
  </main>
</body>
</html>`;
}

function htmlSection(title: string, content: string): string {
  return `<section><h2>${escapeHtml(title)}</h2>${content}</section>`;
}

function htmlMetricGrid(metrics: ReportMetric[]): string {
  return `<div class="grid">${metrics.map((metric) => `<div class="metric"><span>${escapeHtml(metric.label)}</span><strong>${escapeHtml(metric.value)}</strong>${metric.detail ? `<small>${escapeHtml(metric.detail)}</small>` : ""}</div>`).join("")}</div>`;
}

function htmlDefinitionList(metrics: ReportMetric[]): string {
  return `<dl>${metrics.map((metric) => `<div><dt>${escapeHtml(metric.label)}</dt><dd>${escapeHtml(metric.value)}${metric.detail ? `<small>${escapeHtml(metric.detail)}</small>` : ""}</dd></div>`).join("")}</dl>`;
}

function htmlDistribution(title: string, items: ReportDistributionItem[]): string {
  const total = items.reduce((sum, item) => sum + item.value, 0);
  return `<div class="chart"><h3>${escapeHtml(title)}</h3>${items.map((item) => {
    const percent = total > 0 ? Math.round((item.value / total) * 100) : 0;
    return `<div class="bar"><strong>${escapeHtml(item.label)}: ${item.value}</strong><div><span style="--value:${Math.max(percent, item.value > 0 ? 3 : 0)}%"></span></div>${item.detail ? `<small>${escapeHtml(item.detail)}</small>` : ""}</div>`;
  }).join("")}</div>`;
}

function htmlReferenceList(title: string, references: ReportReference[]): string {
  if (references.length === 0) return "";
  return `<article class="item"><h3>${escapeHtml(title)}</h3><ul>${references.map((reference) => `<li><strong>${escapeHtml(reference.label)}</strong>${reference.detail && reference.detail !== reference.label ? ` - ${escapeHtml(reference.detail)}` : ""}</li>`).join("")}</ul></article>`;
}

function htmlItem(title: string, detail: string): string {
  return `<article class="item"><h3>${escapeHtml(title)}</h3><pre>${escapeHtml(detail || "No content recorded.")}</pre></article>`;
}

function drawBox(page: PdfPage, x: number, y: number, width: number, height: number, fill: PdfColor): void {
  page.commands.push(`${rgb(fill)} ${fixed(x)} ${fixed(y)} ${fixed(width)} ${fixed(height)} re f`);
  page.commands.push(`${rgb(COLOR_BORDER).replace("rg", "RG")} ${fixed(x)} ${fixed(y)} ${fixed(width)} ${fixed(height)} re S`);
}

function fontRef(font: PdfFont): string {
  if (font === "bold") return "F2";
  if (font === "mono") return "F3";
  return "F1";
}

function wrapText(value: string, width: number, size: number): string[] {
  const maxChars = Math.max(8, Math.floor(width / (size * 0.52)));
  return String(value || "")
    .replace(/\t/g, "  ")
    .split(/\r?\n/)
    .flatMap((paragraph) => wrapParagraph(paragraph, maxChars));
}

function wrapParagraph(paragraph: string, maxChars: number): string[] {
  if (!paragraph.trim()) return [""];
  const lines: string[] = [];
  let line = "";
  for (const word of paragraph.trim().split(/\s+/)) {
    if (word.length > maxChars) {
      if (line) {
        lines.push(line);
        line = "";
      }
      for (let index = 0; index < word.length; index += maxChars) lines.push(word.slice(index, index + maxChars));
      continue;
    }
    const next = line ? `${line} ${word}` : word;
    if (next.length > maxChars) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function pdfText(value: string): string {
  return `<${[...normalizePdfText(value)].map((character) => winAnsiByte(character).toString(16).toUpperCase().padStart(2, "0")).join("")}>`;
}

function normalizePdfText(value: string): string {
  return String(value)
    .replace(/\r?\n/g, " ")
    .replace(/\t/g, "  ")
    .replace(/\u00A0/g, " ")
    .replace(/\u200B|\u200C|\u200D|\uFEFF/g, "")
    .replace(/\u2212/g, "-")
    .replace(/\u00B7/g, "-")
    .replace(/\u2023|\u25E6|\u2043/g, "-")
    .replace(/\u2713|\u2705/g, "OK")
    .replace(/\u2717|\u274C/g, "X")
    .normalize("NFC");
}

function winAnsiByte(character: string): number {
  const mapped = WIN_ANSI_EXTENDED[character];
  if (mapped) return mapped;

  const codePoint = character.codePointAt(0) ?? 0x3F;
  if ((codePoint >= 0x20 && codePoint <= 0x7E) || (codePoint >= 0xA0 && codePoint <= 0xFF)) {
    return codePoint;
  }

  const fallback = character.normalize("NFKD").replace(/[\u0300-\u036f]/g, "");
  const fallbackCodePoint = fallback.codePointAt(0);
  if (fallbackCodePoint && fallbackCodePoint >= 0x20 && fallbackCodePoint <= 0x7E) {
    return fallbackCodePoint;
  }

  return 0x3F;
}

const WIN_ANSI_EXTENDED: Record<string, number> = {
  "\u20AC": 0x80,
  "\u201A": 0x82,
  "\u0192": 0x83,
  "\u201E": 0x84,
  "\u2026": 0x85,
  "\u2020": 0x86,
  "\u2021": 0x87,
  "\u02C6": 0x88,
  "\u2030": 0x89,
  "\u0160": 0x8A,
  "\u2039": 0x8B,
  "\u0152": 0x8C,
  "\u017D": 0x8E,
  "\u2018": 0x91,
  "\u2019": 0x92,
  "\u201C": 0x93,
  "\u201D": 0x94,
  "\u2022": 0x95,
  "\u2013": 0x96,
  "\u2014": 0x97,
  "\u02DC": 0x98,
  "\u2122": 0x99,
  "\u0161": 0x9A,
  "\u203A": 0x9B,
  "\u0153": 0x9C,
  "\u017E": 0x9E,
  "\u0178": 0x9F,
};

function rgb(color: PdfColor): string {
  return `${fixed(color[0])} ${fixed(color[1])} ${fixed(color[2])} rg`;
}

function fixed(value: number): string {
  return Number(value.toFixed(2)).toString();
}

function byteLength(value: string): number {
  return new TextEncoder().encode(value).length;
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

function escapeHtml(value: string): string {
  return String(value).replace(/[&<>"']/g, (character) => {
    const entities: Record<string, string> = { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" };
    return entities[character];
  });
}

function downloadBlob(content: string, filename: string, type: string): void {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function htmlFilename(report: AssessmentReport): string {
  return `${baseFilename(report)}.html`;
}

function pdfFilename(report: AssessmentReport): string {
  return `${baseFilename(report)}.pdf`;
}

function baseFilename(report: AssessmentReport): string {
  return `assessment-report-${report.runId.slice(0, 8)}`.replace(/[^a-z0-9-]+/gi, "-").toLowerCase();
}
