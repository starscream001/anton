import io
import random
from dataclasses import dataclass
from typing import Optional

import requests
from PIL import Image, ImageStat


@dataclass
class AnalysisResult:
    width: int
    height: int
    dominant_color: str
    description: str


class ImageAnalyzer:
    def __init__(self, model: str = "basic"):
        self.model = model

    def analyze(self, image_url: str) -> AnalysisResult:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGB")
        stat = ImageStat.Stat(image)
        r, g, b = [int(c) for c in stat.mean]
        dominant_color = f"rgb({r}, {g}, {b})"
        width, height = image.size
        description = self._generate_description(width, height, dominant_color)
        return AnalysisResult(
            width=width,
            height=height,
            dominant_color=dominant_color,
            description=description,
        )

    def _generate_description(self, width: int, height: int, color: str) -> str:
        moods = [
            "спокойный",
            "яркий",
            "уютный",
            "динамичный",
            "кинематографичный",
        ]
        mood = random.choice(moods)
        return (
            f"Кадр {width}x{height} с доминирующим оттенком {color}. "
            f"Настроение — {mood}."
        )


def build_caption(analysis: AnalysisResult, platform: str) -> str:
    hashtags = {
        "telegram": "#dailyshot #yandexdisk",
        "vk": "#фото #вдохновение",
        "max": "#photo #inspiration",
    }
    base = (
        f"{analysis.description}\n"
        f"Размер: {analysis.width}x{analysis.height}\n"
        f"Цвет: {analysis.dominant_color}"
    )
    return f"{base}\n\n{hashtags.get(platform, '#photo')}"
