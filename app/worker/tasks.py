import logging
from datetime import datetime

from rq import Queue
from rq.job import Job
from rq.registry import FailedJobRegistry
from redis import Redis

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.post_task import PostTask
from app.services.analyzer import ImageAnalyzer, build_caption
from app.services.publishers import MaxPublisher, TelegramPublisher, VKPublisher
from app.services.yandex import YandexDiskService

settings = get_settings()
redis_conn = Redis.from_url(settings.redis_url)
queue = Queue(connection=redis_conn)
logger = logging.getLogger(__name__)


def enqueue_post(task_id: int) -> Job:
    return queue.enqueue(process_post_task, task_id)


def _get_publisher(platform: str):
    if platform == "telegram":
        return TelegramPublisher()
    if platform == "vk":
        return VKPublisher()
    if platform == "max":
        return MaxPublisher()
    raise ValueError(f"Unsupported platform: {platform}")


def process_post_task(task_id: int) -> None:
    session = SessionLocal()
    task = session.query(PostTask).filter(PostTask.id == task_id).first()
    if not task:
        logger.error("Task %s not found", task_id)
        return

    try:
        task.status = "processing"
        session.commit()

        yandex = YandexDiskService()
        download_url = yandex.get_download_url(task.image_path)
        analyzer = ImageAnalyzer(settings.image_analysis_model)
        analysis = analyzer.analyze(download_url)
        caption = build_caption(analysis, task.platform)

        task.generated_text = caption
        task.image_public_url = download_url
        session.commit()

        if task.requires_confirmation:
            task.status = "awaiting_confirmation"
            session.commit()
            return

        publisher = _get_publisher(task.platform)
        publisher.publish(download_url, caption)

        task.status = "completed"
        task.updated_at = datetime.utcnow()
        session.commit()
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        task.status = "failed"
        task.error_message = str(exc)
        session.commit()
        logger.exception("Failed to process task %s", task_id)
    finally:
        session.close()


def cleanup_failed_jobs() -> None:
    registry = FailedJobRegistry(queue=queue)
    for job_id in registry.get_job_ids():
        registry.remove(job_id, delete_job=True)
