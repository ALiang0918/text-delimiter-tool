from __future__ import annotations

from pathlib import Path
from typing import Iterable
import sys

APP_NAME = "Text Delimiter Tool"


def _default_version_paths() -> list[Path]:
    paths: list[Path] = []

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        paths.append(Path(meipass) / "VERSION")

    module_path = Path(__file__).resolve()
    paths.append(module_path.parents[2] / "VERSION")
    paths.append(Path(sys.executable).resolve().parent / "VERSION")

    return paths


def load_app_version(paths: Iterable[Path] | None = None) -> str:
    for candidate in paths or _default_version_paths():
        if candidate.exists():
            version = candidate.read_text(encoding="utf-8").strip()
            if version:
                return version

    raise FileNotFoundError("Unable to locate VERSION file for application metadata.")


APP_VERSION = load_app_version()
