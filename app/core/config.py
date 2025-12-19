import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


class Settings:
    yandex_api_token: str = os.getenv("YANDEX_API_TOKEN", "")
    yandex_folder_path: str = os.getenv("YANDEX_FOLDER_PATH", "/")

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    vk_access_token: str = os.getenv("VK_ACCESS_TOKEN", "")
    vk_group_id: str = os.getenv("VK_GROUP_ID", "")

    max_api_token: str = os.getenv("MAX_API_TOKEN", "")
    max_api_url: str = os.getenv("MAX_API_URL", "")

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./poster.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    post_confirmation_mode: Literal["auto", "manual"] = os.getenv(
        "POST_CONFIRMATION_MODE", "auto"
    ).lower()  # type: ignore[assignment]
    default_schedule_minutes: int = int(os.getenv("DEFAULT_SCHEDULE_MINUTES", "0"))

    image_analysis_model: str = os.getenv("IMAGE_ANALYSIS_MODEL", "basic")


@lru_cache
def get_settings() -> Settings:
    return Settings()
