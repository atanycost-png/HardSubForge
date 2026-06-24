"""Definições de presets de qualidade para sites de streaming."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class QualityPreset:
    """Classe que define um preset de qualidade."""
    name: str
    description: str
    resolution: str
    bitrate: str
    maxrate: str
    bufsize: str
    preset: str
    audio_bitrate: str = "128k"
    framerate: Optional[int] = None
    
    def get_video_args(self, use_nvenc: bool = True) -> list:
        """Retorna os argumentos de vídeo para FFmpeg."""
        encoder = "h264_nvenc" if use_nvenc else "libx264"
        args = [
            "-map", "0:v:0",
            "-c:v", encoder,
            "-b:v", self.bitrate,
            "-maxrate", self.maxrate,
            "-bufsize", self.bufsize,
            "-preset", self.preset
        ]
        
        if self.framerate:
            args.extend(["-r", str(self.framerate)])
            
        return args
    
    def get_audio_args(self, copy_audio: bool = False) -> list:
        """Retorna os argumentos de áudio para FFmpeg."""
        if copy_audio:
            return ["-c:a", "copy"]
        return ["-c:a", "aac", "-b:a", self.audio_bitrate]


class StreamingPresets:
    """Colecao de presets de qualidade para sites de streaming."""

    MAX_QUALITY = QualityPreset(
        name="Maxima Qualidade",
        description="Arquivamento (1080p, 5500k)",
        resolution="1920:1080",
        bitrate="5500k",
        maxrate="6000k",
        bufsize="11000k",
        preset="p6",
        audio_bitrate="192k"
    )

    STREAMING = QualityPreset(
        name="Streaming Otimizado",
        description="Upload sites (1080p, 4500k)",
        resolution="1920:1080",
        bitrate="4500k",
        maxrate="5000k",
        bufsize="9000k",
        preset="p4",
        audio_bitrate="128k"
    )

    BALANCED = QualityPreset(
        name="Equilibrado",
        description="Bom equilibrio (720p, 2500k)",
        resolution="1280:720",
        bitrate="2500k",
        maxrate="3000k",
        bufsize="5000k",
        preset="p4",
        audio_bitrate="128k"
    )

    COMPACT = QualityPreset(
        name="Economico",
        description="Arquivo leve (480p, 1200k)",
        resolution="854:480",
        bitrate="1200k",
        maxrate="1500k",
        bufsize="2400k",
        preset="p1",
        audio_bitrate="96k"
    )

    @classmethod
    def get_all(cls) -> list[QualityPreset]:
        """Retorna todos os presets disponiveis."""
        return [
            cls.MAX_QUALITY,
            cls.STREAMING,
            cls.BALANCED,
            cls.COMPACT
        ]

    @classmethod
    def get_preset_by_name(cls, name: str) -> Optional[QualityPreset]:
        """Retorna um preset pelo nome."""
        for preset in cls.get_all():
            if preset.name == name:
                return preset
        return None


class CustomPreset:
    """Classe para presets customizados pelo usuário."""
    
    def __init__(self, name: str, resolution: str = "1920:1080",
                 bitrate: str = "4500k", maxrate: str = "",
                 bufsize: str = "", preset: str = "p4",
                 audio_bitrate: str = "128k"):
        self.name = name
        self.resolution = resolution
        self.bitrate = bitrate
        self.maxrate = maxrate or f"{int(bitrate[:-1]) * 1.1:.0f}k"
        self.bufsize = bufsize or f"{int(bitrate[:-1]) * 2:.0f}k"
        self.preset = preset
        self.audio_bitrate = audio_bitrate
    
    def get_video_args(self, use_nvenc: bool = True) -> list:
        """Retorna os argumentos de vídeo para FFmpeg."""
        encoder = "h264_nvenc" if use_nvenc else "libx264"
        return [
            "-map", "0:v:0",
            "-c:v", encoder,
            "-b:v", self.bitrate,
            "-maxrate", self.maxrate,
            "-bufsize", self.bufsize,
            "-preset", self.preset,
            "-vf", f"scale={self.resolution}:force_original_aspect_ratio=decrease,pad={self.resolution}:(ow-iw)/2:(oh-ih)/2"
        ]
    
    def get_audio_args(self, copy_audio: bool = False) -> list:
        """Retorna os argumentos de áudio para FFmpeg."""
        if copy_audio:
            return ["-c:a", "copy"]
        return ["-c:a", "aac", "-b:a", self.audio_bitrate]
    
    def to_dict(self) -> dict:
        """Converte para dicionário para salvar em config."""
        return {
            "name": self.name,
            "resolution": self.resolution,
            "bitrate": self.bitrate,
            "maxrate": self.maxrate,
            "bufsize": self.bufsize,
            "preset": self.preset,
            "audio_bitrate": self.audio_bitrate
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CustomPreset':
        """Cria um preset a partir de um dicionário."""
        return cls(
            name=data["name"],
            resolution=data.get("resolution", "1920:1080"),
            bitrate=data.get("bitrate", "4500k"),
            maxrate=data.get("maxrate", ""),
            bufsize=data.get("bufsize", ""),
            preset=data.get("preset", "p4"),
            audio_bitrate=data.get("audio_bitrate", "128k")
        )
