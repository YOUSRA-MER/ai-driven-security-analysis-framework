"""MySQL persistence for completed assessment history."""

from __future__ import annotations

import json
from typing import Any

from backend.config.settings import get_settings

class AssessmentHistoryStore:
    """Small, synchronous MySQL repository used from async API boundaries."""

    def _connect(self):
        import mysql.connector

        settings = get_settings()
        options: dict[str, Any] = {
            "host": settings.mysql_host,
            "port": settings.mysql_port,
            "user": settings.mysql_user,
            "password": settings.mysql_password,
            "database": settings.mysql_database,
        }
        return mysql.connector.connect(**options)

    def ensure_schema(self) -> None:
        connection = self._connect()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(SCHEMA)
            connection.commit()
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            connection.close()

    def save(self, record: dict[str, Any]) -> None:
        self.ensure_schema()
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO assessments
                (run_id, assessed_at, target_model, target_type, attack_family, objective,
                 risk_score, status, heuristic_result, turns, findings, duration_ms,
                 report_metadata, payload)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE assessed_at=VALUES(assessed_at), target_model=VALUES(target_model),
                 target_type=VALUES(target_type), attack_family=VALUES(attack_family), objective=VALUES(objective),
                 risk_score=VALUES(risk_score), status=VALUES(status), heuristic_result=VALUES(heuristic_result),
                 turns=VALUES(turns), findings=VALUES(findings), duration_ms=VALUES(duration_ms),
                 report_metadata=VALUES(report_metadata), payload=VALUES(payload)""",
                (
                    record["run_id"], record["assessed_at"], record["target_model"], record["target_type"],
                    record["attack_family"], record["objective"], record["risk_score"], record["status"],
                    json.dumps(record["heuristic_result"]), record["turns"], json.dumps(record["findings"]),
                    record["duration_ms"], json.dumps(record["report_metadata"]), json.dumps(record["payload"]),
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def list(self, limit: int = 30) -> list[dict[str, Any]]:
        self.ensure_schema()
        connection = self._connect()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT payload FROM assessments ORDER BY assessed_at DESC LIMIT %s", (limit,))
            summary_fields = {
                "run_id", "status", "phase", "objective", "target", "created_at",
                "updated_at", "error", "summary",
            }
            return [
                {key: value for key, value in json.loads(row["payload"]).items() if key in summary_fields}
                for row in cursor.fetchall()
            ]
        finally:
            connection.close()

    def get(self, run_id: str) -> dict[str, Any] | None:
        self.ensure_schema()
        connection = self._connect()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT payload FROM assessments WHERE run_id=%s", (run_id,))
            row = cursor.fetchone()
            return json.loads(row["payload"]) if row else None
        finally:
            connection.close()

    def delete(self, run_id: str) -> bool:
        self.ensure_schema()
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM assessments WHERE run_id=%s", (run_id,))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()


SCHEMA = """
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""


history_store = AssessmentHistoryStore()
