CREATE TABLE IF NOT EXISTS assessments (
  run_id VARCHAR(64) PRIMARY KEY,
  assessed_at DATETIME(6) NOT NULL,
  target_model VARCHAR(255) NOT NULL,
  target_type VARCHAR(100) NOT NULL,
  attack_family VARCHAR(150) NOT NULL,
  objective TEXT NOT NULL,
  risk_score DECIMAL(6,2) NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL,
  heuristic_result JSON NOT NULL,
  turns INT NOT NULL DEFAULT 0,
  findings JSON NOT NULL,
  duration_ms DECIMAL(12,2) NOT NULL DEFAULT 0,
  report_metadata JSON NOT NULL,
  payload JSON NOT NULL,
  INDEX idx_assessments_date (assessed_at),
  INDEX idx_assessments_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
