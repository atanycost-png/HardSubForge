"""Gerenciamento de configurações da aplicação."""

import json
from pathlib import Path
from typing import List, Optional
from presets.definitions import CustomPreset


class ConfigManager:
    """Gerencia o salvamento e carregamento de configurações."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_path = Path(config_file)
        self.data = self._get_default_config()
        self.load()
    
    def _get_default_config(self) -> dict:
        """Retorna a configuração padrão."""
        return {
            "last_video_dir": "",
            "last_output_dir": "",
            "last_preset": "Máxima Qualidade",
            "last_watermark_text": "",
            "watermark_position": "top",
            "watermark_size": 22,
            "ffmpeg_path": "",
            "use_hardware_accel": True,
            "copy_audio": False,
            "preserve_metadata": True,
            "custom_presets": [],
            "auto_detect_subtitle": True,
            "audio_track": "all"
        }
    
    def load(self):
        """Carrega as configurações do arquivo."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
    
    def save(self):
        """Salva as configurações no arquivo."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")
    
    def get(self, key: str, default=None):
        """Retorna um valor de configuração."""
        return self.data.get(key, default)
    
    def set(self, key: str, value):
        """Define um valor de configuração."""
        self.data[key] = value
    
    def add_custom_preset(self, preset: CustomPreset):
        """Adiciona um preset customizado."""
        custom_presets = self.data.get("custom_presets", [])
        for i, p in enumerate(custom_presets):
            if p["name"] == preset.name:
                custom_presets[i] = preset.to_dict()
                self.save()
                return
        custom_presets.append(preset.to_dict())
        self.save()
    
    def remove_custom_preset(self, name: str):
        """Remove um preset customizado."""
        custom_presets = self.data.get("custom_presets", [])
        self.data["custom_presets"] = [p for p in custom_presets if p["name"] != name]
        self.save()
    
    def get_custom_presets(self) -> List[CustomPreset]:
        """Retorna todos os presets customizados."""
        return [CustomPreset.from_dict(p) for p in self.data.get("custom_presets", [])]
