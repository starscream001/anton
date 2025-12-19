from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.db.session import Base


class PostTask(Base):
    __tablename__ = "post_tasks"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), nullable=False)
    image_path = Column(Text, nullable=False)
    image_public_url = Column(Text, nullable=True)
    generated_text = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    scheduled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    requires_confirmation = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    yandex_resource_name = Column(String(255), nullable=True)
