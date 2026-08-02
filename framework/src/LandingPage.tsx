import { useEffect, useState, type PointerEvent } from "react";
import {
  Activity,
  ArrowRight,
  BrainCircuit,
  Check,
  Gauge,
  ListTree,
  Moon,
  Network,
  Play,
  Server,
  Settings2,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Sun,
  TerminalSquare,
} from "lucide-react";
import { Button, StatusChip } from "./components/ui";

type Theme = "light" | "dark";

function HeroSecurityScene() {
  const attacks = [
    { label: "Prompt injection", x: 350, y: 362 },
    { label: "Jailbreak", x: 500, y: 362 },
    { label: "Prompt leakage", x: 350, y: 418 },
    { label: "Tool abuse", x: 500, y: 418 },
  ];

  return (
    <div className="landing-security-environment">
      <div className="landing-security-plane landing-security-plane--back" />
      <div className="landing-security-frame">
        <span>REDLENS / ACTIVE ASSESSMENT</span><span>RL-042</span>
      </div>
      <svg className="landing-attack-graph" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Attack graph showing an AI planner generating attacks against an LLM target, followed by detection and evidence">
        <defs>
          <pattern id="security-grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M 32 0 L 0 0 0 32" className="landing-graph-grid-line" />
          </pattern>
          <marker id="attack-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" className="landing-graph-arrow" />
          </marker>
        </defs>
        <rect width="800" height="560" fill="url(#security-grid)" />
        <g className="landing-graph-infrastructure">
          <path d="M54 92H746M54 474H746M112 54V506M690 54V506" />
          <path d="M112 92L210 138M690 92L612 132M112 474L225 426M690 474L610 444" />
          <circle cx="112" cy="92" r="3" /><circle cx="690" cy="92" r="3" /><circle cx="112" cy="474" r="3" /><circle cx="690" cy="474" r="3" />
          <circle cx="210" cy="138" r="3" /><circle cx="612" cy="132" r="3" /><circle cx="225" cy="426" r="3" /><circle cx="610" cy="444" r="3" />
        </g>
        <g className="landing-graph-routes">
          {attacks.map((attack) => <path key={attack.label} d={`M234 370 C270 370, 260 ${attack.y}, ${attack.x - 68} ${attack.y}`} />)}
          {attacks.map((attack) => <path key={`${attack.label}-target`} d={`M${attack.x + 68} ${attack.y} C600 ${attack.y}, 608 370, 642 370`} markerEnd="url(#attack-arrow)" />)}
          <path className="landing-graph-route--signal" d="M698 426V480" markerEnd="url(#attack-arrow)" />
          <path className="landing-graph-route--evidence" d="M610 515H580" markerEnd="url(#attack-arrow)" />
        </g>
        <g className="landing-graph-packets">
          <circle r="4"><animateMotion dur="3.8s" repeatCount="indefinite" path="M234 370 C270 370,260 362,282 362 C500 362,610 370,642 370" /></circle>
          <circle r="4"><animateMotion dur="4.4s" begin="-1.8s" repeatCount="indefinite" path="M234 370 C270 370,260 418,282 418 C500 418,610 385,642 370" /></circle>
        </g>
        <g className="landing-graph-node landing-graph-node--planner" transform="translate(88 314)">
          <rect width="146" height="112" rx="8" /><path d="M16 30H130M16 78H130" />
          <text x="18" y="23" className="landing-graph-node-kicker">AI PLANNER</text><text x="18" y="54">Attack strategy</text><text x="18" y="69" className="landing-graph-node-detail">Generating paths</text>
          <circle cx="20" cy="94" r="4" /><text x="31" y="98" className="landing-graph-node-status">ACTIVE</text>
        </g>
        {attacks.map((attack, index) => (
          <g className="landing-graph-attack" transform={`translate(${attack.x - 68} ${attack.y - 18})`} key={attack.label}>
            <rect width="136" height="36" rx="5" /><circle cx="14" cy="18" r="3" /><text x="25" y="22">{attack.label}</text>
            <text x="124" y="22" textAnchor="end">0{index + 1}</text>
          </g>
        ))}
        <g className="landing-graph-node landing-graph-node--target" transform="translate(642 314)">
          <rect width="112" height="112" rx="8" /><path d="M16 30H96M16 78H96" />
          <text x="16" y="23" className="landing-graph-node-kicker">LLM TARGET</text><text x="16" y="54">Application</text><text x="16" y="69" className="landing-graph-node-detail">Monitored</text>
          <circle cx="18" cy="94" r="4" /><text x="29" y="98" className="landing-graph-node-status">ONLINE</text>
        </g>
        <g className="landing-target-scan" transform="translate(698 370)">
          <circle r="78" /><circle r="62" /><circle r="46" />
          <path d="M0-78V-48M78 0H48M0 78V48M-78 0H-48" />
          <path className="landing-target-scan-sweep" d="M0 0L70-35A78 78 0 0 1 78 0Z" />
        </g>
        <g className="landing-graph-node landing-graph-node--signal" transform="translate(610 480)">
          <rect width="144" height="70" rx="8" /><text x="16" y="23" className="landing-graph-node-kicker">SECURITY SIGNAL</text><text x="16" y="45">Vulnerability detected</text><text x="16" y="59" className="landing-graph-node-detail">High confidence</text>
        </g>
        <g className="landing-graph-node landing-graph-node--evidence" transform="translate(420 480)">
          <rect width="160" height="70" rx="8" /><text x="16" y="23" className="landing-graph-node-kicker">EVIDENCE EVENT</text><text x="16" y="45">Instruction disclosure</text><text x="16" y="59" className="landing-graph-node-detail">Transcript captured</text>
        </g>
      </svg>
      <div className="landing-security-hud landing-security-hud--planner"><span>AI PLANNER</span><strong>Generating attack variants</strong><i>05 paths active</i></div>
      <div className="landing-security-hud landing-security-hud--threat"><span>THREAT DETECTED</span><strong>Prompt Injection</strong><i>Confidence 0.94</i></div>
      <div className="landing-security-hud landing-security-hud--path"><span>ATTACK PATH</span><strong>Injection → LLM target</strong></div>
      <div className="landing-security-hud landing-security-hud--evidence"><span>EVIDENCE</span><strong>Response captured</strong><i>Event EV-2841</i></div>
      <div className="landing-security-telemetry"><span><i className="is-ai" /> AI analysis</span><span><i className="is-attack" /> Offensive path</span><span><i className="is-secure" /> Target connected</span></div>
    </div>
  );
}

const capabilityGroups = [
  {
    tone: "attack",
    icon: TerminalSquare,
    eyebrow: "Instruction integrity",
    title: "Protect instruction boundaries",
    description: "Exercise the inputs and retrieved content that can compete with a model's intended instructions.",
    capabilities: ["Prompt Injection", "Indirect Prompt Injection", "Jailbreak", "Roleplay", "RAG Poisoning"],
  },
  {
    tone: "data",
    icon: Network,
    eyebrow: "Data and context",
    title: "Expose unintended disclosure paths",
    description: "Assess the model's ability to protect hidden instructions, sensitive context, and information supplied during a session.",
    capabilities: ["Prompt Leakage", "Context Overflow", "Data Exfiltration"],
  },
  {
    tone: "evasion",
    icon: ShieldAlert,
    eyebrow: "Evasion and execution",
    title: "Challenge the safeguards around use",
    description: "Probe the transformations, languages, and actions that can bypass expected restrictions or approvals.",
    capabilities: ["Encoding", "Multilingual Attacks", "Tool Abuse"],
  },
];

const workflow = [
  { label: "Define assessment", detail: "Set the objective and target model.", icon: Settings2 },
  { label: "AI planner", detail: "Select strategies and generate prompts.", icon: BrainCircuit },
  { label: "Execute attacks", detail: "Run controlled assessment turns.", icon: Play },
  { label: "Analyze security signals", detail: "Evaluate criteria-aware security signals.", icon: Gauge },
  { label: "Review evidence", detail: "Inspect the plan, transcript, and events.", icon: ListTree },
];

export default function LandingPage() {
  const [theme, setTheme] = useState<Theme>(() =>
    window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
  );
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const handleHeroPointerMove = (event: PointerEvent<HTMLElement>) => {
    if (event.pointerType !== "mouse") return;

    const hero = event.currentTarget;
    const bounds = hero.getBoundingClientRect();
    const x = (event.clientX - bounds.left) / bounds.width - 0.5;
    const y = (event.clientY - bounds.top) / bounds.height - 0.5;

    hero.style.setProperty("--hero-pointer-x", `${Math.round(x * 16)}px`);
    hero.style.setProperty("--hero-pointer-y", `${Math.round(y * 12)}px`);
  };

  const resetHeroPointer = (event: PointerEvent<HTMLElement>) => {
    event.currentTarget.style.setProperty("--hero-pointer-x", "0px");
    event.currentTarget.style.setProperty("--hero-pointer-y", "0px");
  };

  return (
    <div className="landing-page">
      <a className="skip-link" href="#landing-main">Skip to main content</a>

      <header className="landing-header">
        <a className="landing-brand" href="/" aria-label="Devoteam RedLens home">
          <span className="landing-brand-mark"><img src="/devoteam-mark.png" alt="" /></span>
          <span className="landing-brand-copy">
            <span>Devoteam</span>
            <strong>RedLens</strong>
          </span>
        </a>

        <nav className="landing-primary-nav" aria-label="Primary navigation">
          <a href="#overview-title">Platform</a>
          <a href="#capabilities-title">Capabilities</a>
          <a href="#workflow-title">How it works</a>
          <a href="#product-title">Product</a>
        </nav>

        <nav className="landing-actions" aria-label="Landing navigation">
          <Button
            variant="ghost"
            size="sm"
            iconOnly
            aria-label={theme === "dark" ? "Use light theme" : "Use dark theme"}
            aria-pressed={theme === "dark"}
            onClick={() => setTheme((current) => current === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun /> : <Moon />}
          </Button>
          <a className="ui-button ui-button--primary ui-button--sm landing-nav-cta" href="/platform">
            <span className="ui-button__content">Launch Platform <ArrowRight /></span>
          </a>
        </nav>
      </header>

      <main id="landing-main" className="landing-main" tabIndex={-1}>
        <section
          className="landing-hero"
          aria-labelledby="landing-title"
          onPointerMove={handleHeroPointerMove}
          onPointerLeave={resetHeroPointer}
        >
          <div className="landing-hero-scene" aria-hidden="true">
            <HeroSecurityScene />
          </div>

          <div className="landing-hero-copy">
            <div className="landing-eyebrow"><Sparkles size={14} aria-hidden="true" /> AI security assessment platform</div>
            <h1 id="landing-title">Assure every interaction with your <span>LLM applications.</span></h1>
            <p className="landing-intro">
              RedLens gives security teams a focused way to test, analyze, and understand LLM application risk—from prompt injection and jailbreaks to prompt leakage and unsafe tool use.
            </p>
            <div className="landing-cta-row">
              <a className="ui-button ui-button--primary ui-button--lg landing-primary-cta" href="/platform">
                <span className="ui-button__content">Launch Platform <ArrowRight /></span>
              </a>
            </div>
            <p className="landing-assurance"><ShieldCheck size={15} aria-hidden="true" /> Built for security teams assessing LLM-powered applications.</p>
          </div>
        </section>

        <section className="landing-section landing-overview" aria-labelledby="overview-title">
          <div className="landing-section-heading">
            <span className="landing-section-kicker">Platform overview</span>
            <h2 id="overview-title">Security testing designed for the way LLM applications behave.</h2>
          </div>
          <div className="landing-overview-layout">
            <div className="landing-overview-narrative">
              <p className="landing-overview-lead">
                RedLens turns an assessment objective into a controlled security workflow. It helps teams move from a question about LLM risk to structured tests, observable security signals, and evidence they can review.
              </p>
              <div className="landing-overview-principles">
                <article>
                  <span className="landing-overview-principle-marker">01</span>
                  <BrainCircuit aria-hidden="true" />
                  <div><strong>Purpose-built planning</strong><p>Generate assessment strategies and prompt variants from the security objective.</p></div>
                </article>
                <article>
                  <span className="landing-overview-principle-marker">02</span>
                  <Activity aria-hidden="true" />
                  <div><strong>Evidence over assumptions</strong><p>Keep the plan, turn-by-turn transcript, events, and heuristic evaluation together.</p></div>
                </article>
              </div>
            </div>
            <div className="landing-overview-map" aria-label="RedLens assessment path from objective to evidence">
              <span className="landing-overview-map-grid" aria-hidden="true" />
              <div className="landing-overview-dashboard-bar">
                <span><i /> Live Status <small>Assessment Status</small></span>
                <strong>Running assessment <small>04:12 elapsed</small></strong>
              </div>
              <div className="landing-overview-dashboard-body">
                <div className="landing-overview-workflow">
                  <article className="landing-overview-flow-card landing-overview-flow-card--input">
                    <span>Assessment input</span>
                    <strong>Security objective</strong>
                    <small>Define the target and intent.</small>
                  </article>
                  <article className="landing-overview-flow-card landing-overview-flow-card--planner">
                    <span>AI Planner</span>
                    <strong>Attack Strategy</strong>
                    <small>Generate focused test paths.</small>
                  </article>
                  <article className="landing-overview-flow-card landing-overview-flow-card--target">
                    <span>LLM Target</span>
                    <strong>Application under test</strong>
                    <small>Monitor model behavior.</small>
                  </article>
                  <article className="landing-overview-flow-card landing-overview-flow-card--evidence">
                    <span>Review surface</span>
                    <strong>Security Evidence</strong>
                    <small>Inspect observable signals.</small>
                  </article>
                </div>
                <aside className="landing-overview-side-panel">
                  <div className="landing-overview-risk">
                    <span>Risk Score</span>
                    <strong>74<small>/100</small></strong>
                    <div className="landing-overview-risk-meter" aria-hidden="true"><i /></div>
                    <small>High confidence signal</small>
                  </div>
                  <div className="landing-overview-events">
                    <span>Live events</span>
                    <p><i /> Prompt variant completed</p>
                    <p><i /> Evidence captured</p>
                    <p><i /> Heuristic evaluation ready</p>
                  </div>
                </aside>
              </div>
            </div>
          </div>
        </section>

        <section className="landing-section landing-capabilities" aria-labelledby="capabilities-title">
          <div className="landing-section-heading landing-section-heading--split">
            <div>
              <span className="landing-section-kicker">Core security capabilities</span>
              <h2 id="capabilities-title">Focused coverage for the risks that matter in LLM applications.</h2>
            </div>
            <p>RedLens groups related attack paths so teams can assess instruction handling, data exposure, and execution safeguards with clear intent.</p>
          </div>
          <div className="landing-capability-board">
            <div className="landing-capability-board-heading">
              <span><ShieldAlert size={16} aria-hidden="true" /> Threat coverage matrix</span>
              <small>Test attack paths across instruction, data, and execution boundaries.</small>
            </div>
            <div className="landing-capability-groups">
              {capabilityGroups.map(({ tone, icon: Icon, eyebrow, title, description, capabilities }) => (
                <article className={`landing-capability-zone landing-capability-zone--${tone}`} key={title}>
                  <header>
                    <span className="landing-capability-icon"><Icon size={19} aria-hidden="true" /></span>
                    <div><span className="landing-card-kicker">{eyebrow}</span><h3>{title}</h3></div>
                  </header>
                  <p>{description}</p>
                  <ul>
                    {capabilities.map((capability, index) => <li key={capability}><span>0{index + 1}</span>{capability}<Check size={14} aria-hidden="true" /></li>)}
                  </ul>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="landing-section landing-workflow" aria-labelledby="workflow-title">
          <div className="landing-section-heading landing-section-heading--center">
            <span className="landing-section-kicker">How RedLens works</span>
            <h2 id="workflow-title">A deliberate path from assessment intent to reviewable evidence.</h2>
          </div>
          <ol className="landing-workflow-pipeline">
            {workflow.map(({ label, detail, icon: Icon }, index) => (
              <li key={label}>
                <span className="landing-workflow-flow" aria-hidden="true" />
                <span className="landing-workflow-icon"><Icon size={19} aria-hidden="true" /></span>
                <div><span className="landing-workflow-step">Stage 0{index + 1}</span><strong>{label}</strong><p>{detail}</p></div>
              </li>
            ))}
          </ol>
        </section>

        <section className="landing-section landing-product" aria-labelledby="product-title">
          <div className="landing-section-heading landing-section-heading--split">
            <div>
              <span className="landing-section-kicker">Product preview</span>
              <h2 id="product-title">One workspace for configuring, running, and reviewing an assessment.</h2>
            </div>
            <p>The console keeps assessment setup beside execution progress and the evidence needed to understand what happened.</p>
          </div>

          <div className="landing-product-frame">
            <div className="landing-product-frame-bar">
              <span><i aria-hidden="true" /> RedLens assessment workspace</span>
              <small>Configure · execute · review</small>
            </div>
            <div className="landing-console">
              <div className="landing-console-config">
                <div className="landing-console-panel-heading"><span>New assessment</span><Settings2 size={16} aria-hidden="true" /></div>
                <div className="landing-console-form">
                  <div className="landing-console-label">Objective</div>
                  <div className="landing-console-objective">Assess whether the target follows injected instructions that conflict with the original task.</div>
                  <div className="landing-console-field"><span>Target model</span><strong><Server size={14} aria-hidden="true" /> llama3.2:3b</strong></div>
                  <div className="landing-console-settings"><span>3 prompt variants</span><span>5 turn limit</span></div>
                  <div className="landing-console-submit"><Play size={15} aria-hidden="true" /> Create assessment</div>
                </div>
              </div>

              <div className="landing-console-workspace">
                <div className="landing-console-workspace-header">
                  <div><span>Live workspace</span><strong>Prompt injection assessment</strong></div>
                  <StatusChip tone="neutral" size="sm" rounded>Awaiting execution</StatusChip>
                </div>
                <div className="landing-console-metrics">
                  <div><span>Planner</span><strong>Ready</strong></div>
                  <div><span>Execution</span><strong>Not started</strong></div>
                  <div><span>Security signals</span><strong>Pending</strong></div>
                </div>
                <div className="landing-console-tabs">
                  <span className="is-active">Summary</span><span>Plan</span><span>Transcript</span><span>Events</span>
                </div>
                <div className="landing-console-empty">
                  <span><ShieldCheck size={22} aria-hidden="true" /></span>
                  <div><strong>Assessment workspace ready</strong><p>Configure the assessment, then execute controlled attack prompts to begin collecting evidence.</p></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="landing-final-cta" aria-labelledby="final-cta-title">
          <div className="landing-final-cta-card">
            <div>
              <span className="landing-section-kicker">Ready when your assessment is</span>
              <h2 id="final-cta-title">Bring LLM security assessment into a clear, controlled workflow.</h2>
              <p>Launch RedLens to define your assessment, test real attack paths, and review the resulting evidence in one workspace.</p>
            </div>
            <a className="ui-button ui-button--primary ui-button--lg landing-final-cta-button" href="/platform">
              <span className="ui-button__content">Launch Platform <ArrowRight /></span>
            </a>
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <a className="landing-brand landing-footer-brand" href="/" aria-label="Devoteam RedLens home">
          <span className="landing-brand-mark"><img src="/devoteam-mark.png" alt="" /></span>
          <span className="landing-brand-copy"><span>Devoteam</span><strong>RedLens</strong></span>
        </a>
        <span className="landing-footer-context">AI security assessment for LLM applications</span>
        <nav className="landing-footer-nav" aria-label="Footer navigation">
          <a href="#landing-main">Back to top</a>
          <a href="/platform">Launch Platform</a>
        </nav>
      </footer>
    </div>
  );
}
