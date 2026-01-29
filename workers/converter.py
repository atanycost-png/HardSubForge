"""Workers de processamento."""

from PySide6.QtCore import QThread, Signal

from ffmpeg.wrapper import FFmpegWrapper, ConversionOptions


class ConversionWorker(QThread):
    """Worker para conversão de vídeo em thread separada."""
    
    progress_signal = Signal(int)
    log_signal = Signal(str)
    finished_signal = Signal(int, str)
    
    def __init__(self, options: ConversionOptions, ffmpeg_wrapper: FFmpegWrapper):
        super().__init__()
        self.options = options
        self.ffmpeg_wrapper = ffmpeg_wrapper
        self._is_cancelled = False
    
    def run(self):
        """Executa a conversão."""
        try:
            returncode = self.ffmpeg_wrapper.convert(
                self.options,
                progress_callback=self._on_progress,
                log_callback=self._on_log
            )
            
            self.finished_signal.emit(returncode, self.options.output_path)
        except Exception as e:
            self.log_signal.emit(f"ERRO CRÍTICO: {str(e)}")
            self.finished_signal.emit(-1, "")
    
    def _on_progress(self, percent: int):
        """Callback de progresso."""
        if not self._is_cancelled:
            self.progress_signal.emit(percent)
    
    def _on_log(self, message: str):
        """Callback de log."""
        if not self._is_cancelled:
            self.log_signal.emit(message)
    
    def stop(self):
        """Cancela a conversão."""
        self._is_cancelled = True
        if self.ffmpeg_wrapper:
            self.ffmpeg_wrapper.stop()


class ProbeWorker(QThread):
    """Worker para obter informações do vídeo."""
    
    finished_signal = Signal(list)
    
    def __init__(self, ffmpeg_wrapper: FFmpegWrapper, video_path: str):
        super().__init__()
        self.ffmpeg_wrapper = ffmpeg_wrapper
        self.video_path = video_path
    
    def run(self):
        """Executa a sondagem do vídeo."""
        audio_streams = self.ffmpeg_wrapper.get_audio_streams(self.video_path)
        self.finished_signal.emit(audio_streams)
