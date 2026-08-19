import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class SISProvider(ABC):
    """Student Information System integration provider."""

    @abstractmethod
    def connect(self, config: dict) -> bool:
        pass

    @abstractmethod
    def fetch_students(self, config: dict) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def health_check(self, config: dict) -> bool:
        pass


class LMSProvider(ABC):
    """Learning Management System integration provider."""

    @abstractmethod
    def connect(self, config: dict) -> bool:
        pass

    @abstractmethod
    def fetch_courses(self, config: dict) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def health_check(self, config: dict) -> bool:
        pass


class CleverSISProvider(SISProvider):
    """Clever SIS integration provider."""

    def connect(self, config: dict) -> bool:
        api_key = config.get("api_key")
        if not api_key:
            logger.error("[CleverSIS] Missing api_key in config")
            return False
        try:
            response = httpx.get(
                "https://api.clever.com/v3.0/me",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception as exc:
            logger.error(f"[CleverSIS] Connection failed: {exc}")
            return False

    def fetch_students(self, config: dict) -> List[Dict[str, Any]]:
        api_key = config.get("api_key", "")
        try:
            response = httpx.get(
                "https://api.clever.com/v3.0/users",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"type": "student"},
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "external_id": s.get("id"),
                        "email": s.get("email"),
                        "first_name": s.get("name", {}).get("first"),
                        "last_name": s.get("name", {}).get("last"),
                        "grade": s.get("student", {}).get("grade"),
                        "school": s.get("student", {}).get("school_name"),
                    }
                    for s in data.get("data", [])
                ]
            return []
        except Exception as exc:
            logger.error(f"[CleverSIS] Fetch students failed: {exc}")
            return []

    def health_check(self, config: dict) -> bool:
        return self.connect(config)


class PowerSchoolSISProvider(SISProvider):
    """PowerSchool SIS integration provider."""

    def connect(self, config: dict) -> bool:
        base_url = config.get("base_url", "")
        client_id = config.get("client_id", "")
        client_secret = config.get("client_secret", "")
        if not all([base_url, client_id, client_secret]):
            logger.error("[PowerSchoolSIS] Missing config fields")
            return False
        try:
            response = httpx.post(
                f"{base_url}/oauth/access_token",
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception as exc:
            logger.error(f"[PowerSchoolSIS] Connection failed: {exc}")
            return False

    def fetch_students(self, config: dict) -> List[Dict[str, Any]]:
        base_url = config.get("base_url", "")
        token = config.get("access_token", "")
        try:
            response = httpx.get(
                f"{base_url}/api/v3/students",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "external_id": str(s.get("id")),
                        "email": s.get("email"),
                        "first_name": s.get("name", {}).get("first_name"),
                        "last_name": s.get("name", {}).get("last_name"),
                        "grade": s.get("grade"),
                        "school": s.get("school"),
                    }
                    for s in data.get("students", [])
                ]
            return []
        except Exception as exc:
            logger.error(f"[PowerSchoolSIS] Fetch students failed: {exc}")
            return []

    def health_check(self, config: dict) -> bool:
        return self.connect(config)


class CanvasLMSProvider(LMSProvider):
    """Canvas LMS integration provider."""

    def connect(self, config: dict) -> bool:
        base_url = config.get("base_url", "")
        api_key = config.get("api_key", "")
        if not base_url or not api_key:
            logger.error("[CanvasLMS] Missing config fields")
            return False
        try:
            response = httpx.get(
                f"{base_url}/api/v1/courses",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception as exc:
            logger.error(f"[CanvasLMS] Connection failed: {exc}")
            return False

    def fetch_courses(self, config: dict) -> List[Dict[str, Any]]:
        base_url = config.get("base_url", "")
        api_key = config.get("api_key", "")
        try:
            response = httpx.get(
                f"{base_url}/api/v1/courses",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"enrollment_type": "student"},
                timeout=30.0,
            )
            if response.status_code == 200:
                return [
                    {
                        "external_id": str(c.get("id")),
                        "name": c.get("name"),
                        "code": c.get("course_code"),
                        "description": c.get("description"),
                    }
                    for c in response.json()
                ]
            return []
        except Exception as exc:
            logger.error(f"[CanvasLMS] Fetch courses failed: {exc}")
            return []

    def health_check(self, config: dict) -> bool:
        return self.connect(config)


class GoogleClassroomLMSProvider(LMSProvider):
    """Google Classroom integration provider."""

    def connect(self, config: dict) -> bool:
        service_account_key = config.get("service_account_key")
        if not service_account_key:
            logger.error("[GoogleClassroom] Missing service_account_key")
            return False
        # In production, use google-api-python-client with service account
        logger.info("[GoogleClassroom] Connection check - configure service account in production")
        return True

    def fetch_courses(self, config: dict) -> List[Dict[str, Any]]:
        # In production, use Google Classroom API
        logger.info("[GoogleClassroom] Fetch courses - implement with google-api-python-client")
        return []

    def health_check(self, config: dict) -> bool:
        return self.connect(config)


# Provider registry
SIS_PROVIDERS = {
    "clever": CleverSISProvider,
    "powerschool": PowerSchoolSISProvider,
}

LMS_PROVIDERS = {
    "canvas": CanvasLMSProvider,
    "google_classroom": GoogleClassroomLMSProvider,
}


def get_sis_provider(provider_name: str) -> Optional[SISProvider]:
    provider_cls = SIS_PROVIDERS.get(provider_name.lower())
    return provider_cls() if provider_cls else None


def get_lms_provider(provider_name: str) -> Optional[LMSProvider]:
    provider_cls = LMS_PROVIDERS.get(provider_name.lower())
    return provider_cls() if provider_cls else None
