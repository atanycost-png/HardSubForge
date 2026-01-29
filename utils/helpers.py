"""Funções auxiliares."""

import re
import shutil
import subprocess
import sys
import platform
import functools
from pathlib import Path
from typing import Optional


LANGUAGE_NAMES = {
    "por": "Português", "eng": "Inglês", "spa": "Espanhol", "fre": "Francês",
    "ger": "Alemão", "ita": "Italiano", "rus": "Russo", "jpn": "Japonês",
    "kor": "Coreano", "chi": "Chinês", "ara": "Árabe", "hin": "Hindi",
    "und": "Desconhecido"
}


@functools.lru_cache(maxsize=128)
def get_language_name(code: str) -> str:
    """Retorna o nome amigável do idioma baseado no código ISO."""
    if not code:
        return "Desconhecido"
    return LANGUAGE_NAMES.get(code.lower(), code)


@functools.lru_cache(maxsize=1)
def get_ffmpeg_binary() -> Optional[str]:
    """Retorna o caminho do binário FFmpeg."""
    script_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))

    if platform.system() == "Windows":
        local_bin = script_dir / "ffmpeg.exe"
    else:
        local_bin = script_dir / "ffmpeg"

    if local_bin.exists():
        return str(local_bin)

    system_bin = shutil.which("ffmpeg")
    if system_bin:
        return system_bin

    return None


@functools.lru_cache(maxsize=1)
def get_ffprobe_binary(ffmpeg_bin_path: Optional[str]) -> Optional[str]:
    """Retorna o caminho do binário FFprobe."""
    if not ffmpeg_bin_path:
        return shutil.which("ffprobe")

    ffprobe_bin = ffmpeg_bin_path.replace("ffmpeg", "ffprobe")
    if Path(ffprobe_bin).exists():
        return ffprobe_bin

    return shutil.which("ffprobe")


@functools.lru_cache(maxsize=1)
def get_font_path() -> Optional[str]:
    """Retorna o caminho para uma fonte compatível."""
    system = platform.system()
    paths = []

    if system == "Windows":
        paths = [
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("C:/Windows/Fonts/calibri.ttf")
        ]
    elif system == "Darwin":
        paths = [
            Path("/Library/Fonts/Arial.ttf"),
            Path("/System/Library/Fonts/Helvetica.ttc"),
            Path("/System/Library/Fonts/Supplemental/Arial.ttf")
        ]
    elif system == "Linux":
        paths = [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/TTF/DejaVuSans.ttf")
        ]

    for p in paths:
        if p.exists():
            return str(p).replace("\\", "/")
    return None


def check_nvidia_gpu() -> bool:
    """Verifica se há uma GPU NVIDIA disponível."""
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            timeout=3,
            creationflags=creationflags
        )
        return result.returncode == 0
    except:
        return False


def escape_filter_text(text: str) -> str:
    """Escapa caracteres especiais para filtros do FFmpeg."""
    text = text.replace("\\", "\\\\\\\\")
    text = text.replace(":", "\\:")
    text = text.replace("'", "\\'")
    text = text.replace("\n", " ")
    text = text.replace("%", "\\%")
    return text


def escape_path_for_filter(path: str) -> str:
    """Escapa caracteres especiais em caminhos para filtros do FFmpeg."""
    path = path.replace("\\", "/")
    path = path.replace(":", "\\:")
    path = path.replace("'", "\\'")
    return path


def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos de nomes de arquivos."""
    pattern = re.compile(r'[<>:"/\\|?*]')
    return pattern.sub('_', filename)
