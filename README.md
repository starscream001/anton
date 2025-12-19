# Автобот для публикации постов из Яндекс.Диска

FastAPI‑сервис, который забирает изображения из указанной папки на Яндекс.Диске, генерирует подписи и публикует посты в Telegram, VK и MAX. Очередь заданий — Redis + RQ, база — PostgreSQL (можно заменить на SQLite через переменную `DATABASE_URL`).

## Быстрый старт

1. Скопируйте переменные окружения:
   ```bash
   cp .env.example .env
   ```
2. Заполните `.env` своими ключами:
   - `YANDEX_API_TOKEN` — OAuth‑токен Яндекс.Диска.
   - `YANDEX_FOLDER_PATH` — путь к папке на диске (например, `/photos/to/post`).
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
   - `VK_ACCESS_TOKEN`, `VK_GROUP_ID`
   - `MAX_API_TOKEN`, `MAX_API_URL`
   - При необходимости поменяйте `DATABASE_URL` и `REDIS_URL`.
3. Запустите стек:
   ```bash
   docker-compose up --build
   ```
4. API будет доступно на `http://localhost:8000` (swagger — `/docs`).

## Основные эндпоинты

- `POST /tasks/schedule` — создать задания на публикацию из папки на Яндекс.Диске.
  ```json
  {
    "platforms": ["telegram", "vk", "max"],
    "limit": 5,
    "schedule_at": null,
    "requires_confirmation": false,
    "yandex_folder_path": "/photos/to/post"
  }
  ```
  - Если `schedule_at` не указан, посты уйдут сразу (или через `DEFAULT_SCHEDULE_MINUTES`).
  - Если `requires_confirmation=true` или `POST_CONFIRMATION_MODE=manual`, задания остановятся в статусе `awaiting_confirmation`.
- `GET /tasks` — список заданий (можно фильтровать по статусу `?status=processing`).
- `POST /tasks/{id}/confirm` — подтверждение отложенной публикации.

## Как это работает

1. `YandexDiskService` берёт список изображений из папки и получает download‑ссылку на каждое. Файлы не изменяются.
2. `ImageAnalyzer` (Pillow) вытаскивает размеры, доминирующий цвет и генерирует лёгкое описание. Хотите более умные тексты — подключите свою модель и используйте переменную `IMAGE_ANALYSIS_MODEL`.
3. Для каждой платформы создаётся `PostTask`, которое попадает в очередь RQ (`Redis`). Worker вызывает соответствующий паблишер:
   - Telegram Bot API (`sendPhoto`)
   - VK API (`wall.post` с прикреплённой ссылкой на изображение)
   - MAX API (произвольный endpoint с `image_url` и `caption`)
4. Опция подтверждения — задания становятся `awaiting_confirmation` и публикуются только после вызова `/tasks/{id}/confirm`.

## Ручной запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
В другом терминале запустите worker:
```bash
python -m app.worker.worker
```
И не забудьте про Redis и базу (можно поменять `DATABASE_URL` на `sqlite:///./poster.db` для локального теста).

## Настройки (переменные окружения)

| Переменная | Описание |
|-----------|----------|
| `YANDEX_API_TOKEN` | OAuth‑токен для доступа к Яндекс.Диску |
| `YANDEX_FOLDER_PATH` | Папка, из которой брать изображения |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Данные бота и чата/канала |
| `VK_ACCESS_TOKEN`, `VK_GROUP_ID` | Токен и ID сообщества VK |
| `MAX_API_TOKEN`, `MAX_API_URL` | Авторизация и URL для MAX |
| `DATABASE_URL` | Подключение к БД (PostgreSQL по умолчанию) |
| `REDIS_URL` | URL Redis |
| `POST_CONFIRMATION_MODE` | `auto` или `manual` |
| `DEFAULT_SCHEDULE_MINUTES` | Отложить публикацию на N минут, если `schedule_at` не задан |
| `IMAGE_ANALYSIS_MODEL` | Имя/тип используемой модели анализа |

## Дополнительно

- Публикация изображений идёт по прямым download‑ссылкам Яндекс.Диска — файлы не изменяются.
- Для продакшн‑VK стоит реализовать полноценную загрузку файла через `photos.getWallUploadServer`, но для простоты здесь используется вложение ссылкой.
- Если нужен доступ к внешним сервисам генерации текста (например, OpenAI), добавьте ключ в `.env` и расширьте `ImageAnalyzer`.
