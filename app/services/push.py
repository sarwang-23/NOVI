import logging
from typing import Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Push notification service using Firebase Cloud Messaging (FCM).
    Configure via environment variables:
      FCM_SERVER_KEY, FCM_SENDER_ID
    """

    @staticmethod
    def _get_fcm_config():
        return {
            "server_key": getattr(settings, "FCM_SERVER_KEY", ""),
            "sender_id": getattr(settings, "FCM_SENDER_ID", ""),
        }

    @staticmethod
    def send_push_notification(
        device_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> bool:
        """
        Send a push notification via FCM.
        Returns True on success, False on failure.
        """
        config = PushNotificationService._get_fcm_config()

        if not config["server_key"]:
            logger.warning("[PushService] FCM server key not configured. Skipping push notification.")
            return False

        try:
            import httpx

            payload = {
                "to": device_token,
                "notification": {
                    "title": title,
                    "body": body,
                },
            }
            if data:
                payload["data"] = data

            response = httpx.post(
                "https://fcm.googleapis.com/fcm/send",
                json=payload,
                headers={
                    "Authorization": f"key={config['server_key']}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                logger.info(f"[PushService] Push notification sent to {device_token[:10]}...")
                return True
            else:
                logger.error(f"[PushService] FCM error {response.status_code}: {response.text}")
                return False

        except ImportError:
            logger.error("[PushService] httpx not installed. Cannot send push notifications.")
            return False
        except Exception as exc:
            logger.error(f"[PushService] Failed to send push notification: {exc}")
            return False

    @staticmethod
    def send_bulk_push(
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> int:
        """Send push notification to multiple devices. Returns count of successful sends."""
        success_count = 0
        for token in device_tokens:
            if PushNotificationService.send_push_notification(token, title, body, data):
                success_count += 1
        return success_count
