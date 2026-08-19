"""
AI/ML Integration Contract for NOVI Backend.

This module defines the interface contract between the NOVI Backend
and the external AI/ML team's service. The backend does NOT implement
any AI/ML logic. It:
  1. Validates and forwards requests to the AI/ML API.
  2. Validates the response.
  3. Persists required results to the database.
  4. Handles errors, timeouts, and audit logging.

AI/ML Base URL is set via the AIML_API_URL environment variable.
"""
import httpx
import logging
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────

AIML_BASE_URL: str = getattr(settings, "AIML_API_URL", "http://localhost:9000")
AIML_TIMEOUT_SECONDS: float = 30.0
AIML_API_KEY: str = getattr(settings, "AIML_API_KEY", "")


# ── Client Factory ────────────────────────────────────────────────────────────

def _get_aiml_client() -> httpx.Client:
    """Returns a configured synchronous HTTP client for the AI/ML service."""
    headers = {"Content-Type": "application/json"}
    if AIML_API_KEY:
        headers["X-API-Key"] = AIML_API_KEY
    return httpx.Client(
        base_url=AIML_BASE_URL,
        headers=headers,
        timeout=AIML_TIMEOUT_SECONDS,
    )


# ── Request Helpers ───────────────────────────────────────────────────────────

def _post(endpoint: str, payload: dict) -> Optional[dict]:
    """
    POST to the AI/ML service.
    Returns parsed JSON on success, None on failure (caller must handle).
    """
    try:
        with _get_aiml_client() as client:
            response = client.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error(f"[AI/ML] Timeout calling {endpoint}")
        return None
    except httpx.HTTPStatusError as exc:
        logger.error(f"[AI/ML] HTTP error {exc.response.status_code} calling {endpoint}: {exc.response.text}")
        return None
    except Exception as exc:
        logger.error(f"[AI/ML] Unexpected error calling {endpoint}: {exc}")
        return None


def _get(endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
    """GET from the AI/ML service."""
    try:
        with _get_aiml_client() as client:
            response = client.get(endpoint, params=params or {})
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error(f"[AI/ML] Timeout calling {endpoint}")
        return None
    except httpx.HTTPStatusError as exc:
        logger.error(f"[AI/ML] HTTP error {exc.response.status_code} calling {endpoint}")
        return None
    except Exception as exc:
        logger.error(f"[AI/ML] Unexpected error calling {endpoint}: {exc}")
        return None


# ── Public Contract Endpoints ─────────────────────────────────────────────────
# These are the ONLY methods the backend should call. Each maps to a documented
# endpoint exposed by the AI/ML team.

class AIMLClient:
    """
    Contract interface between NOVI Backend and the AI/ML team's service.
    Backend sends structured student context; AI/ML returns structured results.
    Backend is responsible for persisting those results.
    """

    @staticmethod
    def get_career_recommendations(student_context: dict) -> Optional[dict]:
        """
        POST /recommendations/careers
        Input:  Student context (goals, skills, interests, grade, curriculum)
        Output: { careers: [{id, name, match_score, reason}], generated_at: str }
        """
        return _post("/recommendations/careers", student_context)

    @staticmethod
    def get_university_recommendations(student_context: dict) -> Optional[dict]:
        """
        POST /recommendations/universities
        Input:  Student context (goals, GPA, curriculum, location_preference)
        Output: { universities: [{id, name, match_score, reason}], generated_at: str }
        """
        return _post("/recommendations/universities", student_context)

    @staticmethod
    def analyze_goal(goal_data: dict) -> Optional[dict]:
        """
        POST /analyze/goal
        Input:  { title, description, goal_type, student_context }
        Output: { quality_score: float, suggestions: [str], risk_flags: [str] }
        """
        return _post("/analyze/goal", goal_data)

    @staticmethod
    def analyze_checkin(checkin_data: dict) -> Optional[dict]:
        """
        POST /analyze/checkin
        Input:  { mood, accomplishments, learnings, student_id }
        Output: { risk_score: float, flags: [str], recommended_actions: [str] }
        """
        return _post("/analyze/checkin", checkin_data)

    @staticmethod
    def generate_roadmap_plan(student_context: dict) -> Optional[dict]:
        """
        POST /planning/roadmap
        Input:  Student context + target goals
        Output: { milestones: [...], weekly_tasks: [...], rationale: str }
        """
        return _post("/planning/roadmap", student_context)

    @staticmethod
    def health_check() -> bool:
        """Check if the AI/ML service is reachable."""
        result = _get("/health")
        return result is not None and result.get("status") == "ok"
