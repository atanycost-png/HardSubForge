"""Widgets reutilizaveis para a interface."""

from enum import Enum, auto
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (QLabel, QPushButton, QMessageBox, QDialog,
                                QVBoxLayout, QHBoxLayout, QFormLayout,
                                QLineEdit, QComboBox, QDialogButtonBox,
                                QFileDialog, QWidget)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor

from ui.styles import Color, Spacing, Radius


class ButtonVariant(Enum):
    """Variantes de estilo do ModernButton."""
    NORMAL = auto()
    DANGER = auto()
    SUCCESS = auto()
    MINIMAL = auto()


class ModernButton(QPushButton):
    """Botao moderno com estados visuais."""

    def __init__(self, text: str, *, variant: ButtonVariant = ButtonVariant.NORMAL,
                 color: str = Color.PRIMARY, hover_color: str = Color.PRIMARY_HOVER,
                 parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._color = color
        self._hover_color = hover_color
        self._variant = variant
        self._apply_styles()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _apply_styles(self) -> None:
        if self._variant == ButtonVariant.NORMAL:
            bg = self._color
            hbg = self._hover_color
        elif self._variant == ButtonVariant.DANGER:
            bg = Color.DANGER
            hbg = Color.DANGER_HOVER
        elif self._variant == ButtonVariant.SUCCESS:
            bg = Color.SUCCESS
            hbg = Color.SUCCESS_HOVER
        else:
            bg = "transparent"
            hbg = Color.BG_LIGHT

        border = "none" if self._variant != ButtonVariant.MINIMAL else f"1px solid {Color.BORDER}"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {Color.TEXT_PRIMARY};
                border-radius: {Radius.MD}px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                border: {border};
            }}
            QPushButton:hover {{
                background-color: {hbg};
            }}
            QPushButton:pressed {{
                background-color: {self._color};
            }}
            QPushButton:disabled {{
                background-color: {Color.BG_MEDIUM};
                color: {Color.TEXT_MUTED};
            }}
        """)


class DropArea(QLabel):
    """Area de drag & drop com suporte a clique."""

    files_dropped = Signal(list)

    IDLE_STYLE = f"""
        QLabel {{
            background-color: {Color.BG_DARK};
            border: 2px dashed {Color.BORDER};
            border-radius: {Radius.LG}px;
            color: {Color.TEXT_SECONDARY};
            padding: 30px;
            min-height: 120px;
            font-size: 14px;
        }}
        QLabel:hover {{
            border-color: {Color.BORDER_HOVER};
            color: {Color.TEXT_PRIMARY};
            background-color: {Color.BG_MEDIUM};
        }}
    """

    ACTIVE_STYLE = IDLE_STYLE.replace(Color.BORDER, Color.BORDER_FOCUS)

    def __init__(self, parent: Optional[QWidget] = None, parent_window: Optional[object] = None):
        super().__init__(parent)
        self.parent_window = parent_window
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Arraste um arquivo de video aqui\nou clique para selecionar")
        self.setStyleSheet(self.IDLE_STYLE)
        self.setAcceptDrops(True)

    def setText(self, text: str) -> None:
        super().setText(text)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            video_exts = ('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm')
            video_files = [u.toLocalFile().lower() for u in urls
                           if u.toLocalFile().lower().endswith(video_exts)]
            if video_files:
                event.accept()
                self.setStyleSheet(self.ACTIVE_STYLE)
                return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self.setStyleSheet(self.IDLE_STYLE)

    @Slot()
    def dropEvent(self, event) -> None:
        self.setStyleSheet(self.IDLE_STYLE)
        video_exts = ('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm')
        video_files = [
            url.toLocalFile() for url in event.mimeData().urls()
            if url.toLocalFile().lower().endswith(video_exts)
        ]
        if video_files:
            self.files_dropped.emit(video_files)

    def mousePressEvent(self, event) -> None:
        if self.parent_window and hasattr(self.parent_window, '_select_video_dialog'):
            self.parent_window._select_video_dialog()


class SectionCard(QWidget):
    """Widget container com estilo de card."""

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        self._layout.setSpacing(Spacing.MD)
        self.setStyleSheet(f"""
            QWidget#section_card {{
                background-color: {Color.BG_CARD};
                border: 1px solid {Color.BORDER};
                border-radius: {Radius.LG}px;
            }}
        """)
        self.setObjectName("section_card")

        if title:
            lbl = QLabel(title)
            lbl.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: {Color.TEXT_SECONDARY};
                padding-bottom: 4px;
                background-color: transparent;
            """)
            self._layout.addWidget(lbl)


class StatusPill(QLabel):
    """Indicador de status tipo pill."""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._color = Color.TEXT_MUTED
        self._bg = Color.BG_MEDIUM
        self._update_style()

    def set_status(self, text: str, color: str, bg: str) -> None:
        self.setText(text)
        self._color = color
        self._bg = bg
        self._update_style()

    def _update_style(self) -> None:
        self.setStyleSheet(f"""
            QLabel {{
                color: {self._color};
                background-color: {self._bg};
                font-size: 11px;
                font-weight: bold;
                padding: 4px 10px;
                border-radius: {Radius.PILL}px;
            }}
        """)


class AddPresetDialog(QDialog):
    """Dialogo para adicionar um novo preset customizado."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Novo Preset Customizado")
        self.setMinimumSize(420, 380)
        self.preset_data = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QFormLayout(self)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ex: Meu Preset HD")
        layout.addRow("Nome do Preset:", self.input_name)

        self.input_resolution = QComboBox()
        self.input_resolution.addItems([
            "1920:1080 (1080p)",
            "1280:720 (720p)",
            "854:480 (480p)"
        ])
        layout.addRow("Resolucao:", self.input_resolution)

        self.input_bitrate = QLineEdit()
        self.input_bitrate.setPlaceholderText("Ex: 4500k")
        layout.addRow("Bitrate (-b:v):", self.input_bitrate)

        self.input_maxrate = QLineEdit()
        self.input_maxrate.setPlaceholderText("Opcional - Ex: 5000k")
        layout.addRow("Maxrate:", self.input_maxrate)

        self.input_bufsize = QLineEdit()
        self.input_bufsize.setPlaceholderText("Opcional - Ex: 9000k")
        layout.addRow("Bufsize:", self.input_bufsize)

        self.combo_preset = QComboBox()
        self.combo_preset.addItems([
            "p1 (Mais Rapido)",
            "p4 (Equilibrado)",
            "p6 (Lento/Melhor)"
        ])
        layout.addRow("Preset NVENC:", self.combo_preset)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                                    QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    @Slot()
    def _validate_and_accept(self) -> None:
        if not self.input_name.text() or not self.input_bitrate.text():
            QMessageBox.warning(self, "Atencao", "Preencha pelo menos o Nome e o Bitrate.")
            return

        if not self._validate_bitrate(self.input_bitrate.text()):
            QMessageBox.warning(self, "Atencao", "O Bitrate deve seguir o formato 'XXXXk' (ex: 4500k)")
            return

        if self.input_maxrate.text() and not self._validate_bitrate(self.input_maxrate.text()):
            QMessageBox.warning(self, "Atencao", "O Maxrate deve seguir o formato 'XXXXk' (ex: 5000k)")
            return

        if self.input_bufsize.text() and not self._validate_bitrate(self.input_bufsize.text()):
            QMessageBox.warning(self, "Atencao", "O Bufsize deve seguir o formato 'XXXXk' (ex: 9000k)")
            return

        preset_code = self.combo_preset.currentText().split()[0]
        resolution = self.input_resolution.currentText().split()[0]

        from presets.definitions import CustomPreset
        self.preset_data = CustomPreset(
            name=self.input_name.text(),
            resolution=resolution,
            bitrate=self.input_bitrate.text(),
            maxrate=self.input_maxrate.text(),
            bufsize=self.input_bufsize.text(),
            preset=preset_code
        )
        self.accept()

    def _validate_bitrate(self, value: str) -> bool:
        import re
        return bool(re.match(r'^\d+k$', value))

    def get_preset_data(self):
        return self.preset_data