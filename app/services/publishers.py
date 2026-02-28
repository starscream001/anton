import logging
from typing import Optional

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TelegramPublisher:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_chat_id

    def publish(self, image_url: str, caption: str) -> None:
        api_url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        response = requests.post(
            api_url,
            data={"chat_id": self.chat_id, "caption": caption},
            files={"photo": ("image.jpg", image_response.content)},
            timeout=30,
        )
        if not response.ok:
            raise RuntimeError(f"Telegram error: {response.text}")


class VKPublisher:
    def __init__(self, token: Optional[str] = None, group_id: Optional[str] = None):
        self.token = token or settings.vk_access_token
        self.group_id = group_id or settings.vk_group_id

    def publish(self, image_url: str, caption: str) -> None:
        # Simplified workflow: assumes a helper API endpoint exists for direct wall posting.
        # In production, you should upload the photo to a server upload URL first.
        api_url = "https://api.vk.com/method/wall.post"
        payload = {
            "owner_id": f"-{self.group_id}",
            "message": caption,
            "attachments": image_url,
            "access_token": self.token,
            "v": "5.199",
        }
        response = requests.post(api_url, data=payload, timeout=30)
        if not response.ok:
            raise RuntimeError(f"VK error: {response.text}")
        resp_json = response.json()
        if "error" in resp_json:
            raise RuntimeError(f"VK API error: {resp_json['error']}")


class MaxPublisher:
    def __init__(self, token: Optional[str] = None, api_url: Optional[str] = None):
        self.token = token or settings.max_api_token
        self.api_url = api_url or settings.max_api_url

    def publish(self, image_url: str, caption: str) -> None:
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        payload = {"caption": caption, "image_url": image_url}
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        if not response.ok:
            raise RuntimeError(f"MAX error: {response.text}")
