from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, HTTPException

from app.api.schemas import ScheduleRequest, TaskResponse
from app.core.config import get_settings
from app.db.session import get_session
from app.models.post_task import PostTask
from app.services.yandex import YandexDiskService
from app.worker.tasks import enqueue_post

router = APIRouter()
settings = get_settings()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/tasks/schedule", response_model=List[TaskResponse])
def schedule_posts(payload: ScheduleRequest):
    yandex = YandexDiskService()
    images = yandex.list_images(folder_path=payload.yandex_folder_path, limit=payload.limit)
    if not images:
        raise HTTPException(status_code=404, detail="Images not found in folder")

    scheduled_at = payload.schedule_at
    if not scheduled_at and settings.default_schedule_minutes > 0:
        scheduled_at = datetime.utcnow() + timedelta(minutes=settings.default_schedule_minutes)

    new_tasks: List[TaskResponse] = []
    with get_session() as session:
        for image in images:
            for platform in payload.platforms:
                task = PostTask(
                    platform=platform,
                    image_path=image["path"],
                    status="scheduled" if scheduled_at else "queued",
                    scheduled_at=scheduled_at,
                    requires_confirmation=payload.requires_confirmation
                    or settings.post_confirmation_mode == "manual",
                    yandex_resource_name=image.get("name"),
                )
                session.add(task)
                session.commit()
                session.refresh(task)
                enqueue_post(task.id)
                new_tasks.append(TaskResponse.from_orm(task))

    return new_tasks


@router.get("/tasks", response_model=List[TaskResponse])
def list_tasks(status: str | None = None):
    with get_session() as session:
        query = session.query(PostTask)
        if status:
            query = query.filter(PostTask.status == status)
        tasks = query.order_by(PostTask.created_at.desc()).all()
        return [TaskResponse.from_orm(t) for t in tasks]


@router.post("/tasks/{task_id}/confirm", response_model=TaskResponse)
def confirm_task(task_id: int):
    with get_session() as session:
        task = session.query(PostTask).filter(PostTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status != "awaiting_confirmation":
            raise HTTPException(status_code=400, detail="Task not awaiting confirmation")

        from app.worker.tasks import process_post_task

        process_post_task(task_id)
        session.refresh(task)
        return TaskResponse.from_orm(task)
