export type RunStatus =
  | "queued"
  | "planning"
  | "awaiting_execution"
  | "executing"
  | "completed"
  | "partial"
  | "failed"
  | "interrupted"
  | "cancelling";

export interface OllamaModel {
  name: string;
  size: number;
  modified_at: string | null;
  digest: string;
}

export interface PlatformStatus {
  planner: {
    provider: string;
    configured: boolean;
    model: string;
  };
  ollama: {
    reachable: boolean;
    base_url: string;
    models: OllamaModel[];
    error: string;
  };
  active_runs: number;
  timestamp: string;
}

export interface RunEvent {
  id: number;
  type: string;
  phase: string;
  level: "info" | "warning" | "error";
  message: string;
  timestamp: string;
  data: Record<string, unknown>;
}

export interface GeneratedPrompt {
  id: string;
  content: string;
  objective: string;
  strategy_id: string;
  attack_family: string;
  asset_ids: string[];
  turn: number;
  confidence?: number;
  metadata?: Record<string, unknown>;
}

export interface RejectedPrompt {
  prompt_id: string;
  sequence_index: number;
  attack_family: string;
  reasons: string[];
  preview: string;
}

export interface PlannerView {
  success: boolean;
  stage: string;
  confidence: number;
  confidence_level: string;
  warnings: string[];
  errors: string[];
  selected_attack_family: string;
  selected_strategy: string;
  reasoning_summary: string;
  plan_id: string;
  steps: Array<Record<string, unknown>>;
  generated_prompts: GeneratedPrompt[];
  rejected_prompts: RejectedPrompt[];
  requested_prompt_count: number;
  candidate_prompt_count: number;
  trace: string[];
  elapsed_ms: number | null;
}

export interface ExecutionError {
  code: string;
  message: string;
  turn_number: number | null;
  attempt: number | null;
  retryable: boolean;
  timestamp: string;
}

export interface ExecutionTurn {
  turn_number: number;
  prompt: string;
  response: string;
  provider: string;
  model: string;
  latency_ms: number;
  timestamp: string;
  status: "success" | "error" | "interrupted";
  metadata: Record<string, unknown>;
}

export interface ExecutionResult {
  execution_id: string;
  planner_id: string;
  objective: string;
  provider: string;
  model: string;
  execution_status: string;
  conversation_history: ExecutionTurn[];
  responses: string[];
  execution_metrics: {
    planned_turns: number;
    attempted_turns: number;
    successful_turns: number;
    failed_turns: number;
    provider_calls: number;
    retry_count: number;
    average_latency_ms: number;
    minimum_latency_ms: number;
    maximum_latency_ms: number;
    token_usage: Record<string, number>;
    started_at: string;
    ended_at: string;
  };
  total_latency: number;
  total_turns: number;
  errors: ExecutionError[];
  warnings: string[];
  metadata: Record<string, unknown>;
}

export interface HeuristicEvaluation {
  turn_number: number;
  score: number;
  label: string;
  reason: string;
  evidence: string[];
  heuristic: boolean;
  heuristic_type?: "criteria_aware" | string;
}

export interface RunSummary {
  attack_family: string;
  strategy: string;
  planner_confidence: number;
  successful_turns: number;
  failed_turns: number;
  total_turns: number;
  total_latency_ms: number;
  maximum_heuristic_score: number;
  requested_prompts: number;
  accepted_prompts: number;
  rejected_prompts: number;
  max_turns: number;
  heuristic_label: "pending" | "signal_detected" | "no_signal" | "inconclusive";
}

export interface AttackRun {
  run_id: string;
  status: RunStatus;
  phase: string;
  objective: string;
  target: {
    provider: string;
    model: string;
    base_url: string;
  };
  created_at: string;
  updated_at: string;
  error: string;
  summary: RunSummary;
  request?: RunRequest;
  events?: RunEvent[];
  planner?: PlannerView | null;
  execution?: ExecutionResult | null;
  heuristic_evaluation?: HeuristicEvaluation[];
}

export interface RunRequest {
  objective: string;
  target_model: string;
  target_base_url: string;
  target_type: string;
  auto_execute: boolean;
  prompt_count: number;
  max_turns: number;
  max_retries: number;
  timeout_seconds: number;
  temperature: number;
  max_output_tokens: number;
  continue_on_error: boolean;
  use_controlled_system_prompt: boolean;
}
