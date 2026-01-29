"""Widgets reutilizáveis para a interface."""

from pathlib import Path

from PySide6.QtWidgets import (QLabel, QPushButton, QProgressBar, 
                               QMessageBox, QDialog, QVBoxLayout, 
                               QHBoxLayout, QFormLayout, QSpinBox,
                               QLineEdit, QComboBox, QDialogButtonBox,
                               QFileDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette


class ModernButton(QPushButton):
    """Botão moderno com estilo personalizado."""
    
    def __init__(self, text: str, color: str = "#4A90E2", hover_color: str = "#357ABD"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; border-radius: 8px; padding: 10px; font-weight: bold; font-size: 14px; border: none; }}
            QPushButton:hover {{ background-color: {hover_color}; }}
            QPushButton:disabled {{ background-color: #444; color: #888; }}
        """)
        self.setCursor(Qt.PointingHandCursor)


class DropArea(QLabel):
    """Área de drag & drop para arquivos."""
    
    files_dropped = Signal(list)
    
    def __init__(self, parent=None, parent_window=None):
        super().__init__(parent)
        self.parent_window = parent_window
        self.setAlignment(Qt.AlignCenter)
        self.setText("Arraste um arquivo de vídeo aqui\nou clique para selecionar")
        self.setStyleSheet("""
            QLabel { background-color: #2B2B2B; border: 2px dashed #555; border-radius: 10px; color: #AAA; padding: 30px; min-height: 120px; }
            QLabel:hover { border-color: #4A90E2; color: #FFF; background-color: #333; }
        """)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            video_files = [u.toLocalFile().lower() for u in urls 
                          if u.toLocalFile().lower().endswith(('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv'))]
            if video_files:
                event.accept()
                self.setStyleSheet(self.styleSheet().replace("#555", "#4A90E2"))
                return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("#4A90E2", "#555"))
    
    def dropEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("#4A90E2", "#555"))
        video_files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv')):
                video_files.append(file_path)
        if video_files:
            self.files_dropped.emit(video_files)
    
    def mousePressEvent(self, event):
        if self.parent_window and hasattr(self.parent_window, '_select_video_dialog'):
            self.parent_window._select_video_dialog()


class AddPresetDialog(QDialog):
    """Diálogo para adicionar um novo preset customizado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Preset Customizado")
        self.setFixedSize(400, 350)
        self.preset_data = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ex: Meu Preset HD")
        layout.addRow("Nome do Preset:", self.input_name)
        
        self.input_resolution = QComboBox()
        self.input_resolution.addItems([
            "1920:1080 (1080p)",
            "1280:720 (720p)",
            "854:480 (480p)"
        ])
        layout.addRow("Resolução:", self.input_resolution)
        
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
        self.combo_preset.addItems(["p1 (Mais Rápido)", "p4 (Equilibrado)", "p6 (Lento/Melhor)"])
        layout.addRow("Preset NVENC:", self.combo_preset)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def validate_and_accept(self):
        if not self.input_name.text() or not self.input_bitrate.text():
            QMessageBox.warning(self, "Atenção", "Preencha pelo menos o Nome e o Bitrate.")
            return
        
        if not self._validate_bitrate(self.input_bitrate.text()):
            QMessageBox.warning(self, "Atenção", "O Bitrate deve seguir o formato 'XXXXk' (ex: 4500k)")
            return
        
        if self.input_maxrate.text() and not self._validate_bitrate(self.input_maxrate.text()):
            QMessageBox.warning(self, "Atenção", "O Maxrate deve seguir o formato 'XXXXk' (ex: 5000k)")
            return
        
        if self.input_bufsize.text() and not self._validate_bitrate(self.input_bufsize.text()):
            QMessageBox.warning(self, "Atenção", "O Bufsize deve seguir o formato 'XXXXk' (ex: 9000k)")
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
        """Valida formato do bitrate."""
        import re
        return bool(re.match(r'^\d+k$', value))
    
    def get_preset_data(self):
        return self.preset_data
