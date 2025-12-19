from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ScheduleRequest(BaseModel):
    platforms: List[Literal["telegram", "vk", "max"]]
    schedule_at: Optional[datetime] = Field(
        None, description="UTC datetime when the post should go live"
    )
    requires_confirmation: bool = False
    limit: int = Field(5, le=50, description="Max number of images to schedule")
    yandex_folder_path: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    platform: str
    image_path: str
    status: str
    scheduled_at: Optional[datetime]
    requires_confirmation: bool
    generated_text: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True
