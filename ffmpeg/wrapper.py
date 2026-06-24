"""Wrapper para FFmpeg - usando a lógica do código original."""

import re
import subprocess
import platform
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

from presets.definitions import QualityPreset, CustomPreset
from utils.helpers import get_ffmpeg_binary, get_ffprobe_binary, escape_filter_text, escape_path_for_filter, check_nvidia_gpu


TIME_PATTERN = re.compile(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})')
DURATION_PATTERN = re.compile(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})')


@dataclass
class ConversionOptions:
    """Opções de conversão de vídeo."""
    
    input_path: str
    output_path: str
    preset: QualityPreset | CustomPreset
    subtitle_path: Optional[str] = None
    subtitle_stream_index: Optional[int] = None
    subtitle_burn: bool = False
    custom_bitrate: Optional[str] = None
    watermark_text: str = ""
    watermark_position: str = "top"
    watermark_size: int = 22
    audio_track_index: Optional[int] = None
    use_hardware_accel: bool = True
    copy_audio: bool = False
    preserve_metadata: bool = True


class FFmpegWrapper:
    """Wrapper para FFmpeg com suporte a legendas e watermark."""
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg_path = ffmpeg_path or get_ffmpeg_binary()
        self.ffprobe_path = get_ffprobe_binary(self.ffmpeg_path)
        self.font_path = self._get_font_path()
        self._is_cancelled = False
        self.process = None
        self.output_path = ""
    
    def _get_font_path(self) -> Optional[str]:
        """Retorna o caminho da fonte."""
        from utils.helpers import get_font_path
        return get_font_path()
    
    def _has_nvidia_gpu(self) -> bool:
        """Verifica se há GPU NVIDIA."""
        return check_nvidia_gpu()
    
    def get_audio_streams(self, video_path: str) -> List[Dict]:
        """Retorna as faixas de audio do video (compatibilidade)."""
        return self.get_streams(video_path).get("audio", [])

    def get_streams(self, video_path: str) -> Dict[str, List[Dict]]:
        """Retorna faixas de audio e legendas do video."""
        result = {"audio": [], "subtitles": []}
        if not self.ffprobe_path:
            return result
        
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            video_path
        ]
        
        try:
            proc_result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc_result.returncode == 0:
                import json
                data = json.loads(proc_result.stdout)
                
                for s in data.get("streams", []):
                    codec_type = s.get("codec_type", "")
                    index = s.get("index", 0)
                    codec = s.get("codec_name", "unk").upper()
                    tags = s.get("tags", {})
                    
                    lang_code = tags.get("language") or tags.get("title") or ""
                    from utils.helpers import get_language_name
                    lang_name = get_language_name(lang_code) if lang_code else ""
                    
                    if codec_type == "audio":
                        if not lang_name:
                            channels = s.get("channels", "unknown")
                            lang_name = f"{channels} Canais"
                        result["audio"].append({
                            "index": index,
                            "title": f"Track {index}: {lang_name} ({codec})",
                            "codec": codec,
                            "language": lang_name
                        })
                    
                    elif codec_type == "subtitle":
                        if not lang_name:
                            lang_name = codec

                        disposition = s.get("disposition", {})
                        title_tag = tags.get("title", "").lower()

                        if disposition.get("forced", 0) == 1 or "forced" in title_tag:
                            sub_type = "Forcada"
                        elif disposition.get("visual_impaired", 0) == 1 or "descriptive" in title_tag:
                            sub_type = "AD"
                        elif disposition.get("hearing_impaired", 0) == 1 or "sdh" in title_tag:
                            sub_type = "SDH"
                        elif disposition.get("default", 0) == 1:
                            sub_type = "Padrao"
                        else:
                            sub_type = "Normal"

                        result["subtitles"].append({
                            "index": index,
                            "title": f"Track {index}: {lang_name} ({codec}) [{sub_type}]",
                            "codec": codec.lower(),
                            "language": lang_name
                        })
                
        except Exception as e:
            print(f"Erro ao obter streams: {e}")
            import traceback
            traceback.print_exc()
        
        return result

    def get_duration(self, video_path: str) -> float:
        """Retorna a duracao do video em segundos."""
        if not self.ffprobe_path:
            return 0.0

        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            video_path
        ]

        try:
            proc_result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc_result.returncode == 0:
                import json
                data = json.loads(proc_result.stdout)
                return float(data.get("format", {}).get("duration", 0))
        except Exception:
            pass

        return 0.0

    def generate_preview(self, options: ConversionOptions, output_path: str,
                         seek_seconds: float = 10.0) -> bool:
        """Gera um frame de preview com filtros aplicados."""
        if not self.ffmpeg_path:
            return False

        cmd = self.build_command(options)
        preview_cmd = [
            self.ffmpeg_path, "-y",
            "-ss", str(seek_seconds),
            "-i", options.input_path,
            "-vframes", "1",
            "-q:v", "2"
        ]

        filter_complex = None
        filter_parts = []

        scale_filter = f"scale={options.preset.resolution}:force_original_aspect_ratio=decrease,pad={options.preset.resolution}:(ow-iw)/2:(oh-ih)/2"
        filter_parts.append(scale_filter)

        if options.watermark_text and self.font_path:
            safe_text = escape_filter_text(options.watermark_text)
            pos_map = {"top": "y=20", "center": "y=(h-text_h)/2", "bottom": "y=h-text_h-20"}
            y_pos = pos_map.get(options.watermark_position, "y=20")
            safe_font = escape_path_for_filter(self.font_path)
            drawtext = (f"drawtext=fontfile='{safe_font}':text='{safe_text}':fontcolor=white@0.9:fontsize={options.watermark_size}:box=1:boxcolor=black@0.4:boxborderw=10:x=(w-text_w)/2:{y_pos}")
            filter_parts.append(drawtext)

        if options.subtitle_burn:
            if options.subtitle_path and Path(options.subtitle_path).exists():
                safe_sub = escape_path_for_filter(options.subtitle_path)
                filter_parts.append(f"subtitles='{safe_sub}'")
            elif options.subtitle_stream_index is not None:
                safe_input = escape_path_for_filter(options.input_path)
                filter_parts.append(f"subtitles='{safe_input}':si={options.subtitle_stream_index}")

        if filter_parts:
            preview_cmd.extend(["-vf", ",".join(filter_parts)])

        preview_cmd.append(output_path)

        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            result = subprocess.run(preview_cmd, capture_output=True, timeout=30,
                                     creationflags=creation_flags)
            return result.returncode == 0 and Path(output_path).exists()
        except Exception:
            return False
    
    def build_command(self, options: ConversionOptions) -> List[str]:
        """Constrói o comando FFmpeg usando a lógica original."""
        cmd = [self.ffmpeg_path, "-y", "-err_detect", "ignore_err", "-fflags", "+genpts"]
        
        if options.use_hardware_accel and self._has_nvidia_gpu():
            cmd.extend(["-hwaccel", "cuda"])
        
        cmd.extend(["-i", options.input_path])
        
        filter_parts = []
        
        # Adiciona filtro de escala
        scale_filter = f"scale={options.preset.resolution}:force_original_aspect_ratio=decrease,pad={options.preset.resolution}:(ow-iw)/2:(oh-ih)/2"
        filter_parts.append(scale_filter)
        
        # Adiciona watermark se houver
        if options.watermark_text and self.font_path:
            safe_text = escape_filter_text(options.watermark_text)
            pos_map = {
                "top": "y=20",
                "center": "y=(h-text_h)/2",
                "bottom": "y=h-text_h-20"
            }
            y_pos = pos_map.get(options.watermark_position, "y=20")
            safe_font = escape_path_for_filter(self.font_path)
            drawtext = (f"drawtext=fontfile='{safe_font}':text='{safe_text}':fontcolor=white@0.9:fontsize={options.watermark_size}:box=1:boxcolor=black@0.4:boxborderw=10:x=(w-text_w)/2:{y_pos}")
            filter_parts.append(drawtext)
        
        # Adiciona legenda (externa ou embutida)
        if options.subtitle_burn:
            if options.subtitle_path and Path(options.subtitle_path).exists():
                safe_sub = escape_path_for_filter(options.subtitle_path)
                filter_parts.append(f"subtitles='{safe_sub}'")
            elif options.subtitle_stream_index is not None:
                safe_input = escape_path_for_filter(options.input_path)
                filter_parts.append(f"subtitles='{safe_input}':si={options.subtitle_stream_index}")
        
        # Aplica filtros se houver
        if filter_parts:
            filter_complex = f"[0:v]{','.join(filter_parts)}[vout]"
            cmd.extend(["-filter_complex", filter_complex, "-map", "[vout]"])
        else:
            cmd.extend(["-map", "0:v"])
        
        # Mapeamento de áudio - exatamente como no código original
        if options.audio_track_index is not None:
            cmd.extend(["-map", f"0:{options.audio_track_index}"])
        else:
            cmd.extend(["-map", "0:a?"])
        
        # Encoder de vídeo
        if options.use_hardware_accel and self._has_nvidia_gpu():
            cmd.extend(["-c:v", "h264_nvenc", "-preset", options.preset.preset])
        else:
            cmd.extend(["-c:v", "libx264", "-preset", "medium"])
        
        # Encoder de áudio
        if options.copy_audio:
            cmd.extend(["-c:a", "copy"])
        else:
            cmd.extend(["-c:a", "aac", "-b:a", options.preset.audio_bitrate])
        
        # Parâmetros de bitrate
        bitrate_val = options.custom_bitrate if options.custom_bitrate else options.preset.bitrate
        cmd.extend([
            "-rc", "vbr",
            "-b:v", bitrate_val,
            "-maxrate", options.preset.maxrate,
            "-bufsize", options.preset.bufsize,
            "-profile:v", "high",
            "-pix_fmt", "yuv420p"
        ])
        
        # Metadados
        if options.preserve_metadata:
            cmd.extend(["-map_metadata", "0"])
        
        cmd.extend(["-movflags", "+faststart", options.output_path])
        
        return cmd
    
    def convert(self, options: ConversionOptions, progress_callback=None, log_callback=None) -> int:
        """Executa a conversão usando a lógica original. Retorna o returncode do processo."""
        if not self.ffmpeg_path:
            if log_callback:
                log_callback("ERRO: FFmpeg não encontrado")
            return -1
        
        self.options = options
        self.output_path = options.output_path
        self._is_cancelled = False
        cmd = self.build_command(options)
        
        if log_callback:
            log_callback(f"Comando: {' '.join(cmd)}")
        
        total_duration = 0
        creation_flags = 0
        
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NO_WINDOW
        
        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace', creationflags=creation_flags
            )
            
            last_percent = -1
            for line in self.process.stdout:
                # Skip emitting progress updates to log to save UI resources
                if "time=" not in line.strip():
                    if log_callback:
                        log_callback(line.strip())
                
                # Use string membership checks before regex to reduce CPU overhead in hot loop
                if total_duration == 0:
                    if "Duration:" in line.strip():
                        d_match = DURATION_PATTERN.search(line.strip())
                        if d_match:
                            h, m, s = map(float, d_match.groups())
                            total_duration = h * 3600 + m * 60 + s
                            continue # Skip time search for the same line
                
                else: # total_duration > 0
                    if "time=" in line.strip():
                        t_match = TIME_PATTERN.search(line.strip())
                        if t_match:
                            h, m, s = map(float, t_match.groups())
                            current_time = h * 3600 + m * 60 + s
                            percent = min(int((current_time / total_duration) * 100), 99)
                            # Optimization: Only emit signal when percentage changes to avoid flooding the UI thread
                            if percent != last_percent:
                                if progress_callback:
                                    progress_callback(percent)
                                last_percent = percent
            
            self.process.wait()
            returncode = self.process.returncode
            
            if progress_callback:
                progress_callback(100)
            
            return -2 if self._is_cancelled else returncode
        except Exception as e:
            if log_callback:
                log_callback(f"ERRO CRÍTICO: {str(e)}")
            if progress_callback:
                progress_callback(100)
            return -1
    
    def stop(self):
        """Cancela a conversao - usando a logica original."""
        self._is_cancelled = True
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
