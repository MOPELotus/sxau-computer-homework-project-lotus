from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    api_key: str = os.getenv("SILICONFLOW_API_KEY", "").strip()
    api_base_url: str = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1").strip().rstrip("/")
    chat_model: str = os.getenv("SILICONFLOW_CHAT_MODEL", "Qwen/Qwen3.5-397B-A17B").strip()
    request_timeout: int = int(os.getenv("SILICONFLOW_TIMEOUT", "60"))
    default_materials_dir: Path = ROOT_DIR / "materials" / "source"
    default_output_dir: Path = ROOT_DIR / "artifacts" / "latest"

    @property
    def api_enabled(self) -> bool:
        return bool(self.api_key)


def get_settings() -> Settings:
    return Settings()
