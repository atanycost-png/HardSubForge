"""Workers de processamento com thread-safety."""

from typing import List, Dict, Optional, Callable, Any

from PySide6.QtCore import QObject, Signal, Slot, QMutex, QMutexLocker, QThread, QTimer

from ffmpeg.wrapper import FFmpegWrapper, ConversionOptions


class ConversionWorker(QObject):
    """Worker para conversao de video (padrao QObject + moveToThread)."""

    progress_signal = Signal(int)
    log_signal = Signal(str)
    finished_signal = Signal(int, str)

    def __init__(self, options: ConversionOptions, ffmpeg_wrapper: FFmpegWrapper):
        super().__init__()
        self.options = options
        self.ffmpeg_wrapper = ffmpeg_wrapper
        self._mutex = QMutex()
        self._cancelled = False

    @Slot()
    def run(self) -> None:
        """Executa a conversao."""
        try:
            returncode = self.ffmpeg_wrapper.convert(
                self.options,
                progress_callback=self._on_progress,
                log_callback=self._on_log
            )
            self.finished_signal.emit(returncode, self.options.output_path)
        except Exception as e:
            self.log_signal.emit(f"ERRO CRITICO: {str(e)}")
            import traceback
            traceback.print_exc()
            self.finished_signal.emit(-1, "")

    def _on_progress(self, percent: int) -> None:
        """Callback de progresso (thread-safe via signal)."""
        with QMutexLocker(self._mutex):
            if self._cancelled:
                return
        self.progress_signal.emit(percent)

    def _on_log(self, message: str) -> None:
        """Callback de log (thread-safe via signal)."""
        with QMutexLocker(self._mutex):
            if self._cancelled:
                return
        self.log_signal.emit(message)

    @Slot()
    def stop(self) -> None:
        """Cancela a conversao com seguranca de thread."""
        with QMutexLocker(self._mutex):
            self._cancelled = True
        if self.ffmpeg_wrapper:
            self.ffmpeg_wrapper.stop()


class ProbeWorker(QObject):
    """Worker para obter informacoes do video."""

    finished_signal = Signal(dict)

    def __init__(self, ffmpeg_wrapper: FFmpegWrapper, video_path: str):
        super().__init__()
        self.ffmpeg_wrapper = ffmpeg_wrapper
        self.video_path = video_path

    @Slot()
    def run(self) -> None:
        """Executa a sondagem do video."""
        try:
            streams = self.ffmpeg_wrapper.get_streams(self.video_path)
            self.finished_signal.emit(streams)
        except Exception as e:
            self.finished_signal.emit({"audio": [], "subtitles": []})
