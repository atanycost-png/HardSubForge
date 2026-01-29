"""Janela principal da aplicação."""

import sys
import platform
from pathlib import Path

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QComboBox, QTextEdit, QCheckBox,
                               QSpinBox, QLineEdit, QFileDialog, QMessageBox,
                               QSystemTrayIcon, QMenu, QProgressBar, QPushButton,
                               QApplication)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QPalette, QIcon, QDesktopServices

from config.config_manager import ConfigManager
from presets.definitions import StreamingPresets, CustomPreset
from ffmpeg.wrapper import FFmpegWrapper, ConversionOptions
from workers.converter import ConversionWorker, ProbeWorker
from ui.widgets import ModernButton, DropArea, AddPresetDialog
from utils.helpers import check_nvidia_gpu, get_ffmpeg_binary


class MainWindow(QMainWindow):
    """Janela principal do HardSubForge."""
    
    APP_VERSION = "3.0.0"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"HardSubForge v{self.APP_VERSION}")
        self.resize(900, 950)
        
        self.config = ConfigManager()
        self.video_path = ""
        self.subtitle_path = ""
        self.output_path = ""
        self.output_filename = ""
        
        self.ffmpeg_wrapper = FFmpegWrapper(self.config.get("ffmpeg_path"))
        self.worker = None
        self.probe_worker = None
        self.has_nvidia = check_nvidia_gpu()
        
        self._setup_ui()
        self._apply_theme()
        self._load_settings()
        self._setup_tray_icon()
        self._update_status_ui()
        
        if not self.ffmpeg_wrapper.ffmpeg_path:
            self._show_ffmpeg_warning()
    
    def _setup_ui(self):
        """Configura a interface do usuário."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addWidget(self._create_header())
        layout.addWidget(self._create_status_bar())
        layout.addWidget(self._create_video_selection())
        layout.addWidget(self._create_subtitle_section())
        layout.addWidget(self._create_audio_section())
        layout.addWidget(self._create_watermark_section())
        layout.addWidget(self._create_preset_section())
        layout.addWidget(self._create_output_section())
        layout.addWidget(self._create_options_section())
        layout.addWidget(self._create_progress_section())
        layout.addWidget(self._create_buttons())
        layout.addWidget(self._create_log_section())
    
    def _create_header(self) -> QLabel:
        """Cria o cabeçalho."""
        header = QLabel("HardSubForge")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #4A90E2;")
        header.setAlignment(Qt.AlignCenter)
        return header
    
    def _create_status_bar(self) -> QWidget:
        """Cria a barra de status."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_ffmpeg_status = QLabel("FFmpeg: --")
        self.lbl_ffmpeg_status.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.lbl_ffmpeg_status)
        
        gpu_text = "GPU: NVIDIA Detectada" if self.has_nvidia else "GPU: Não detectada"
        self.lbl_gpu_status = QLabel(gpu_text)
        self.lbl_gpu_status.setStyleSheet(f"color: {'#4CAF50' if self.has_nvidia else '#FFA726'}; font-size: 11px;")
        layout.addWidget(self.lbl_gpu_status)
        
        self.lbl_encoder = QLabel("Encoder: --")
        self.lbl_encoder.setStyleSheet("color: #AAA; font-size: 11px;")
        layout.addWidget(self.lbl_encoder)
        
        layout.addStretch()
        
        return widget
    
    def _create_video_selection(self) -> QWidget:
        """Cria a seção de seleção de vídeo."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("Arquivo de Entrada:"))
        self.drop_area = DropArea(parent_window=self)
        self.drop_area.files_dropped.connect(self._on_files_dropped)
        layout.addWidget(self.drop_area)
        
        return widget
    
    def _create_subtitle_section(self) -> QWidget:
        """Cria a seção de legenda."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_subtitle = QLabel("Legenda: Nenhuma selecionada")
        self.lbl_subtitle.setStyleSheet("color: #AAA;")
        layout.addWidget(self.lbl_subtitle)
        
        btn_select = QPushButton("Selecionar")
        btn_select.setStyleSheet("background-color: transparent; border: 1px solid #555; color: #CCC; padding: 5px;")
        btn_select.clicked.connect(self._select_subtitle)
        layout.addWidget(btn_select)
        
        btn_clear = QPushButton("Limpar")
        btn_clear.setStyleSheet("background-color: transparent; border: 1px solid #555; color: #CCC; padding: 5px;")
        btn_clear.clicked.connect(self._clear_subtitle)
        layout.addWidget(btn_clear)
        
        return widget
    
    def _create_audio_section(self) -> QWidget:
        """Cria a seção de áudio."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_audio = QLabel("Áudio:")
        self.lbl_audio.setStyleSheet("color: #AAA;")
        layout.addWidget(self.lbl_audio)
        
        self.combo_audio = QComboBox()
        self.combo_audio.setStyleSheet("background-color: #2B2B2B; color: white; padding: 5px;")
        layout.addWidget(self.combo_audio)
        
        return widget
    
    def _create_watermark_section(self) -> QWidget:
        """Cria a seção de watermark."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("Watermark/Texto Superior:"))
        
        text_layout = QHBoxLayout()
        self.entry_watermark = QLineEdit()
        self.entry_watermark.setPlaceholderText("Digite o texto aqui...")
        self.entry_watermark.setStyleSheet("background-color: #2B2B2B; color: white; padding: 8px; border-radius: 6px;")
        text_layout.addWidget(self.entry_watermark)
        
        self.spin_watermark_size = QSpinBox()
        self.spin_watermark_size.setRange(10, 72)
        self.spin_watermark_size.setValue(22)
        self.spin_watermark_size.setPrefix("Tamanho: ")
        self.spin_watermark_size.setStyleSheet("background-color: #2B2B2B; color: white; padding: 5px;")
        text_layout.addWidget(self.spin_watermark_size)
        
        layout.addLayout(text_layout)
        
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Posição:"))
        self.combo_watermark_pos = QComboBox()
        self.combo_watermark_pos.addItems(["Topo", "Centro", "Rodapé"])
        self.combo_watermark_pos.setCurrentText("Topo")
        self.combo_watermark_pos.setStyleSheet("background-color: #2B2B2B; color: white; padding: 5px;")
        pos_layout.addWidget(self.combo_watermark_pos)
        pos_layout.addStretch()
        layout.addLayout(pos_layout)
        
        return widget
    
    def _create_preset_section(self) -> QWidget:
        """Cria a seção de presets."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("Preset de Qualidade:"))
        
        self.combo_preset = QComboBox()
        self.combo_preset.setStyleSheet("background-color: #2B2B2B; color: white; padding: 8px;")
        self._load_presets()
        layout.addWidget(self.combo_preset)
        
        btn_add = QPushButton("+")
        btn_add.setFixedSize(30, 30)
        btn_add.setToolTip("Criar novo Preset")
        btn_add.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px; border: none;")
        btn_add.clicked.connect(self._add_preset)
        layout.addWidget(btn_add)
        
        btn_delete = QPushButton("-")
        btn_delete.setFixedSize(30, 30)
        btn_delete.setToolTip("Deletar Preset")
        btn_delete.setStyleSheet("background-color: #D32F2F; color: white; font-weight: bold; border-radius: 5px; border: none;")
        btn_delete.clicked.connect(self._delete_preset)
        layout.addWidget(btn_delete)
        
        return widget
    
    def _create_output_section(self) -> QWidget:
        """Cria a seção de saída."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("Arquivo de Saída:"))
        
        path_layout = QHBoxLayout()
        self.entry_output_path = QLineEdit()
        self.entry_output_path.setPlaceholderText("Caminho de saída (opcional)")
        self.entry_output_path.setStyleSheet("background-color: #2B2B2B; color: white; padding: 8px; border-radius: 6px;")
        path_layout.addWidget(self.entry_output_path)
        
        btn_browse = QPushButton("📁")
        btn_browse.setFixedSize(35, 35)
        btn_browse.setToolTip("Selecionar pasta de saída")
        btn_browse.setStyleSheet("background-color: #4A90E2; color: white; border-radius: 5px; border: none;")
        btn_browse.clicked.connect(self._browse_output_path)
        path_layout.addWidget(btn_browse)
        
        layout.addLayout(path_layout)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nome do arquivo:"))
        
        self.entry_output_name = QLineEdit()
        self.entry_output_name.setPlaceholderText("Nome do arquivo (opcional - usa nome original)")
        self.entry_output_name.setStyleSheet("background-color: #2B2B2B; color: white; padding: 8px; border-radius: 6px;")
        name_layout.addWidget(self.entry_output_name)
        
        layout.addLayout(name_layout)
        
        return widget
    
    def _create_options_section(self) -> QWidget:
        """Cria a seção de opções."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.chk_hw_accel = QCheckBox("Usar aceleração por hardware (NVIDIA NVENC)")
        self.chk_hw_accel.setChecked(self.has_nvidia)
        self.chk_hw_accel.setEnabled(self.has_nvidia)
        self.chk_hw_accel.setStyleSheet("color: #CCC;")
        layout.addWidget(self.chk_hw_accel)
        
        self.chk_copy_audio = QCheckBox("Copiar áudio sem reencode (mais rápido)")
        self.chk_copy_audio.setChecked(False)
        self.chk_copy_audio.setStyleSheet("color: #CCC;")
        layout.addWidget(self.chk_copy_audio)
        
        self.chk_metadata = QCheckBox("Preservar metadados do vídeo original")
        self.chk_metadata.setChecked(True)
        self.chk_metadata.setStyleSheet("color: #CCC;")
        layout.addWidget(self.chk_metadata)
        
        return widget
    
    def _create_progress_section(self) -> QProgressBar:
        """Cria a barra de progresso."""
        from PySide6.QtWidgets import QProgressBar
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { 
                border: 1px solid #444; 
                border-radius: 5px; 
                text-align: center; 
                color: white; 
                height: 25px; 
                background-color: #1E1E1E;
            } 
            QProgressBar::chunk { background-color: #4A90E2; }
        """)
        return self.progress_bar
    
    def _create_buttons(self) -> QWidget:
        """Cria os botões de ação."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_convert = ModernButton("INICIAR CONVERSÃO", "#4CAF50", "#45A049")
        self.btn_convert.clicked.connect(self._start_conversion)
        self.btn_convert.setFixedHeight(45)
        layout.addWidget(self.btn_convert)
        
        self.btn_cancel = ModernButton("CANCELAR", "#D32F2F", "#B71C1C")
        self.btn_cancel.clicked.connect(self._cancel_conversion)
        self.btn_cancel.setFixedHeight(45)
        self.btn_cancel.setEnabled(False)
        layout.addWidget(self.btn_cancel)
        
        return widget
    
    def _create_log_section(self) -> QWidget:
        """Cria a seção de log."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("Log de Conversão:"))
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("""
            background-color: #121212; 
            color: #00FF00; 
            font-family: Consolas, monospace; 
            font-size: 10px;
        """)
        self.txt_log.setMaximumHeight(150)
        self.txt_log.document().setMaximumBlockCount(1000)
        layout.addWidget(self.txt_log)
        
        return widget
    
    def _apply_theme(self):
        """Aplica o tema escuro."""
        qapp = QApplication.instance()
        qapp.setStyle("Fusion")
        
        palette = qapp.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1E1E1E"))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor("#252525"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1E1E1E"))
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#4A90E2"))
        qapp.setPalette(palette)
    
    def _setup_tray_icon(self):
        """Configura o ícone da bandeja do sistema."""
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = Path(__file__).parent.parent / "icon.ico"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        self.tray_icon.show()
    
    def _update_status_ui(self):
        """Atualiza a UI de status."""
        if self.ffmpeg_wrapper.ffmpeg_path:
            self.lbl_ffmpeg_status.setText(f"FFmpeg: OK")
            self.lbl_ffmpeg_status.setStyleSheet("color: #4CAF50; font-size: 11px;")
            encoder = "NVENC" if self.chk_hw_accel.isChecked() else "CPU (libx264)"
            self.lbl_encoder.setText(f"Encoder: {encoder}")
        else:
            self.lbl_ffmpeg_status.setText("FFmpeg: NÃO ENCONTRADO")
            self.lbl_ffmpeg_status.setStyleSheet("color: #F44336; font-size: 11px; font-weight: bold;")
            self.lbl_encoder.setText("Encoder: --")
    
    def _load_settings(self):
        """Carrega as configurações salvas."""
        last_dir = self.config.get("last_video_dir")
        if last_dir:
            self._last_video_dir = last_dir
        
        last_output_dir = self.config.get("last_output_dir")
        if last_output_dir:
            self.entry_output_path.setText(last_output_dir)
        
        watermark_text = self.config.get("last_watermark_text", "")
        self.entry_watermark.setText(watermark_text)
        
        watermark_size = self.config.get("watermark_size", 22)
        self.spin_watermark_size.setValue(watermark_size)
        
        watermark_pos = self.config.get("watermark_position", "top")
        pos_map = {"top": "Topo", "center": "Centro", "bottom": "Rodapé"}
        self.combo_watermark_pos.setCurrentText(pos_map.get(watermark_pos, "Topo"))
        
        self.chk_hw_accel.setChecked(self.config.get("use_hardware_accel", True))
        self.chk_copy_audio.setChecked(self.config.get("copy_audio", False))
        self.chk_metadata.setChecked(self.config.get("preserve_metadata", True))
        
        last_preset = self.config.get("last_preset", "Máxima Qualidade")
        index = self.combo_preset.findText(last_preset)
        if index >= 0:
            self.combo_preset.setCurrentIndex(index)
    
    def _save_settings(self):
        """Salva as configurações."""
        self.config.set("last_watermark_text", self.entry_watermark.text())
        self.config.set("watermark_size", self.spin_watermark_size.value())
        
        pos_map = {"Topo": "top", "Centro": "center", "Rodapé": "bottom"}
        self.config.set("watermark_position", pos_map.get(self.combo_watermark_pos.currentText(), "top"))
        
        self.config.set("use_hardware_accel", self.chk_hw_accel.isChecked())
        self.config.set("copy_audio", self.chk_copy_audio.isChecked())
        self.config.set("preserve_metadata", self.chk_metadata.isChecked())
        self.config.set("last_preset", self.combo_preset.currentText())
        
        if self.output_path:
            self.config.set("last_output_dir", self.output_path)
        
        if self.video_path:
            self.config.set("last_video_dir", str(Path(self.video_path).parent))
        
        self.config.save()
    
    def _load_presets(self):
        """Carrega os presets no combo box."""
        self.combo_preset.blockSignals(True)
        self.combo_preset.clear()
        
        for preset in StreamingPresets.get_all():
            self.combo_preset.addItem(f"🎬 {preset.name}", preset)
        
        for preset in self.config.get_custom_presets():
            self.combo_preset.addItem(f"⚙️ {preset.name}", preset)
        
        self.combo_preset.blockSignals(False)
    
    def _on_files_dropped(self, files):
        """Manipula arquivos arrastados."""
        if files:
            self._load_video(files[0])
    
    def _select_video_dialog(self):
        """Abre o diálogo para selecionar um vídeo."""
        last_dir = self.config.get("last_video_dir", "")
        if not last_dir:
            last_dir = str(Path.home())
        
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecione o arquivo de vídeo",
            last_dir,
            "Vídeos (*.mp4 *.mkv *.avi *.mov *.wmv *.flv);;Todos os arquivos (*.*)"
        )
        
        if path:
            self._load_video(path)
    
    def _load_video(self, path):
        """Carrega um vídeo."""
        self.video_path = path
        self.drop_area.setText(f"📁 {Path(path).name}")
        self.drop_area.setStyleSheet(self.drop_area.styleSheet().replace("#555", "#4A90E2"))
        
        self._detect_subtitle(path)
        self._probe_audio_and_subtitles(path)
        
        if not self.entry_output_name.text():
            self.entry_output_name.setText(Path(path).stem + "_converted")
        
        if not self.output_path:
            self.entry_output_path.setText(str(Path(path).parent))
    
    def _detect_subtitle(self, video_path):
        """Detecta legenda externa automaticamente."""
        video_dir = Path(video_path).parent
        video_name = Path(video_path).stem
        
        for ext in ['.srt', '.ass', '.ssa']:
            subtitle_path = video_dir / (video_name + ext)
            if subtitle_path.exists():
                self.subtitle_path = str(subtitle_path)
                self.lbl_subtitle.setText(f"Legenda: {subtitle_path.name}")
                self.lbl_subtitle.setStyleSheet("color: #4CAF50;")
                return
        
        self.subtitle_path = ""
        self.lbl_subtitle.setText("Legenda: Nenhuma detectada")
        self.lbl_subtitle.setStyleSheet("color: #AAA;")
    
    def _probe_audio_and_subtitles(self, video_path):
        """Obtém faixas de áudio e legendas do vídeo."""
        self.probe_worker = ProbeWorker(self.ffmpeg_wrapper, video_path)
        self.probe_worker.finished_signal.connect(self._on_audio_and_subtitles_probed)
        self.probe_worker.start()
    
    def _on_audio_and_subtitles_probed(self, streams):
        """Manipula resultado da sondagem de áudio."""
        self.combo_audio.clear()
        self.combo_audio.addItem("Padrão (Todas as faixas)", None)
        
        if streams:
            self.lbl_audio.setText("Áudio:")
            self.combo_audio.setEnabled(True)
            for s in streams:
                self.combo_audio.addItem(s['title'], s['index'])
        else:
            self.lbl_audio.setText("Áudio: Nenhuma faixa detectada")
            self.combo_audio.setEnabled(False)
    
    def _select_subtitle(self):
        """Seleciona uma legenda manualmente."""
        if not self.video_path:
            return
        
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecione a Legenda",
            str(Path(self.video_path).parent),
            "Legendas (*.srt *.ass *.ssa);;Todos os arquivos (*.*)"
        )
        
        if path:
            self.subtitle_path = path
            self.lbl_subtitle.setText(f"Legenda: {Path(path).name}")
            self.lbl_subtitle.setStyleSheet("color: #4CAF50;")
    
    def _clear_subtitle(self):
        """Limpa a legenda selecionada."""
        self.subtitle_path = ""
        self.lbl_subtitle.setText("Legenda: Nenhuma selecionada")
        self.lbl_subtitle.setStyleSheet("color: #AAA;")
    
    def _browse_output_path(self):
        """Seleciona o caminho de saída."""
        path = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        if path:
            self.entry_output_path.setText(path)
    
    def _add_preset(self):
        """Adiciona um novo preset."""
        dialog = AddPresetDialog(self)
        if dialog.exec():
            preset = dialog.get_preset_data()
            if preset:
                self.config.add_custom_preset(preset)
                self._load_presets()
                self.combo_preset.setCurrentText(f"⚙️ {preset.name}")
                QMessageBox.information(self, "Sucesso", f"Preset '{preset.name}' salvo!")
    
    def _delete_preset(self):
        """Deleta o preset selecionado."""
        current_text = self.combo_preset.currentText()
        
        if not current_text.startswith("⚙️"):
            QMessageBox.information(self, "Info", "Apenas presets customizados podem ser deletados.")
            return
        
        name = current_text[2:]
        reply = QMessageBox.question(
            self, "Deletar Preset",
            f"Deseja realmente deletar o preset '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.remove_custom_preset(name)
            self._load_presets()
            QMessageBox.information(self, "Sucesso", f"Preset '{name}' deletado!")
    
    def _start_conversion(self):
        """Inicia a conversão."""
        if not self.video_path:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo de vídeo primeiro.")
            return
        
        if not self.ffmpeg_wrapper.ffmpeg_path:
            QMessageBox.warning(self, "Aviso", "FFmpeg não encontrado. Configure o caminho nas configurações.")
            return
        
        output_path = self.entry_output_path.text() or str(Path(self.video_path).parent)
        output_name = self.entry_output_name.text() or (Path(self.video_path).stem + "_converted")
        output_full = str(Path(output_path) / f"{output_name}.mp4")
        
        preset_data = self.combo_preset.currentData()
        
        audio_map = {
            "Todas as faixas": "all",
            "Primeira faixa": "first",
            "Sem áudio": "none"
        }
        
        pos_map = {"Topo": "top", "Centro": "center", "Rodapé": "bottom"}
        
        audio_track_index = self.combo_audio.currentData()
        
        options = ConversionOptions(
            input_path=self.video_path,
            output_path=output_full,
            preset=preset_data,
            subtitle_path=self.subtitle_path,
            watermark_text=self.entry_watermark.text(),
            watermark_position=pos_map.get(self.combo_watermark_pos.currentText(), "top"),
            watermark_size=self.spin_watermark_size.value(),
            audio_track_index=audio_track_index,
            use_hardware_accel=self.chk_hw_accel.isChecked(),
            copy_audio=self.chk_copy_audio.isChecked(),
            preserve_metadata=self.chk_metadata.isChecked()
        )
        
        self._save_settings()
        
        self.btn_convert.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.worker = ConversionWorker(options, self.ffmpeg_wrapper)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.log_signal.connect(self._log)
        self.worker.finished_signal.connect(self._on_conversion_finished)
        self.worker.start()
    
    def _cancel_conversion(self):
        """Cancela a conversão - simplificado sem confirmação."""
        if self.worker:
            self._log("Cancelando conversão...")
            self.worker.stop()
    
    def _on_conversion_finished(self, success, message):
        """Manipula o término da conversão."""
        self.btn_convert.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        
        if success == 0:
            self.progress_bar.setValue(100)
            self._log(f"✅ Conversão concluída com sucesso!")
            self._log(f"📁 Arquivo salvo: {message}")
            
            reply = QMessageBox.question(
                self, "Conversão Concluída",
                f"Conversão finalizada!\n\nArquivo: {Path(message).name}\n\nDeseja abrir a pasta do arquivo?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(message).parent)))
            
            if self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "HardSubForge",
                    "Conversão finalizada!",
                    QSystemTrayIcon.Information,
                    3000
                )
        else:
            self._log(f"❌ Erro na conversão: {message}")
            QMessageBox.critical(self, "Erro", f"Erro na conversão:\n{message}")
    
    def _log(self, message):
        """Adiciona uma mensagem ao log."""
        self.txt_log.append(message)
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())
    
    def _show_ffmpeg_warning(self):
        """Mostra aviso de FFmpeg não encontrado."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("FFmpeg Não Encontrado")
        msg.setText("O FFmpeg é necessário para a conversão de vídeos.")
        msg.setInformativeText("Você pode baixá-lo automaticamente (apenas Windows) ou selecioná-lo manualmente.")
        
        btn_download = msg.addButton("Baixar Automaticamente", QMessageBox.ActionRole)
        btn_manual = msg.addButton("Selecionar Manualmente", QMessageBox.ActionRole)
        msg.addButton("Cancelar", QMessageBox.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == btn_download:
            if platform.system() == "Windows":
                self._download_ffmpeg_windows()
            else:
                QMessageBox.information(self, "Info", "Download automático disponível apenas para Windows.")
        elif msg.clickedButton() == btn_manual:
            self._select_ffmpeg_manual()
    
    def _download_ffmpeg_windows(self):
        """Baixa o FFmpeg automaticamente (apenas Windows)."""
        pass
    
    def _select_ffmpeg_manual(self):
        """Seleciona o FFmpeg manualmente."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecione o executável do FFmpeg",
            "", "Executáveis (*.exe);;Todos os arquivos (*.*)" if platform.system() == "Windows" else "Todos os arquivos (*.*)"
        )
        
        if path and Path(path).exists():
            self.config.set("ffmpeg_path", path)
            self.config.save()
            self.ffmpeg_wrapper = FFmpegWrapper(path)
            self._update_status_ui()
            QMessageBox.information(self, "Sucesso", "FFmpeg configurado com sucesso!")
