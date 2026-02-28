import logging

from rq import Connection, Worker

from app.core.config import get_settings
from app.worker.tasks import queue, redis_conn


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    with Connection(redis_conn):
        worker = Worker([queue])
        worker.work(with_scheduler=False)


if __name__ == "__main__":
    main()
