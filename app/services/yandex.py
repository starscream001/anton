from typing import List, Optional

import requests

from app.core.config import get_settings

settings = get_settings()


class YandexDiskService:
    API_BASE = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.yandex_api_token

    @property
    def headers(self) -> dict:
        return {"Authorization": f"OAuth {self.token}"}

    def list_images(self, folder_path: Optional[str] = None, limit: int = 10) -> List[dict]:
        path = folder_path or settings.yandex_folder_path
        params = {"path": path, "limit": limit}
        response = requests.get(
            f"{self.API_BASE}/resources", headers=self.headers, params=params, timeout=20
        )
        response.raise_for_status()
        data = response.json()
        embedded = data.get("_embedded", {})
        items = embedded.get("items", [])
        return [item for item in items if item.get("media_type") == "image"]

    def get_download_url(self, resource_path: str) -> str:
        response = requests.get(
            f"{self.API_BASE}/resources/download",
            headers=self.headers,
            params={"path": resource_path},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return data["href"]
