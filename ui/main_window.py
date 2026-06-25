"""Janela principal da aplicacao."""

import platform
from pathlib import Path
from typing import Optional, List
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QComboBox, QTextEdit, QCheckBox,
                                QSpinBox, QLineEdit, QFileDialog, QMessageBox,
                                QSystemTrayIcon, QMenu, QProgressBar, QPushButton,
                                QApplication, QScrollArea, QSlider, QDialog)
from PySide6.QtCore import Qt, Signal, Slot, QUrl, QThread, QTimer, QPoint
from PySide6.QtGui import QIcon, QDesktopServices, QMouseEvent, QPixmap

from config.config_manager import ConfigManager
from presets.definitions import StreamingPresets, CustomPreset
from ffmpeg.wrapper import FFmpegWrapper, ConversionOptions
from workers.converter import ConversionWorker, ProbeWorker
from ui.widgets import ModernButton, DropArea, AddPresetDialog, SectionCard, StatusPill, ButtonVariant, BatchItem, BatchQueueCard
from ui.styles import Color, Spacing, Radius
from ui.theme import apply_dark_theme, apply_light_theme
from utils.helpers import check_nvidia_gpu, get_ffmpeg_binary, is_text_subtitle


class MainWindow(QMainWindow):
    """Janela principal do HardSubForge."""

    APP_VERSION = "3.1.0"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"HardSubForge v{self.APP_VERSION}")
        self.resize(960, 1000)
        self.setMinimumSize(800, 700)

        self.config = ConfigManager()
        self.video_path = ""
        self.subtitle_path = ""
        self.output_path = ""
        self.output_filename = ""

        self.ffmpeg_wrapper = FFmpegWrapper(self.config.get("ffmpeg_path"))
        self._worker = None
        self._worker_thread = None
        self._probe_worker = None
        self._probe_thread = None
        self.has_nvidia = check_nvidia_gpu()

        self._autoscroll_active = False
        self._autoscroll_start = QPoint()
        self._autoscroll_initial = 0
        self._subtitle_card = None
        self._scroll_area = None
        self._dark_theme = True

        self.batch_queue: List[BatchItem] = []
        self._batch_selected_index: int = -1
        self._batch_processing: bool = False
        self._probe_generation: int = 0
        self._batch_card = None

        self._setup_ui()
        self._load_settings()
        self._setup_tray_icon()
        self._update_status_ui()

        if not self.ffmpeg_wrapper.ffmpeg_path:
            self._show_ffmpeg_warning()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        apply_dark_theme(QApplication.instance())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll_area = scroll
        self._scroll_area.viewport().installEventFilter(self)
        self.setCentralWidget(scroll)

        central = QWidget()
        central.setObjectName("central_widget")
        scroll.setWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)

        layout.addWidget(self._create_header())
        layout.addLayout(self._create_status_bar())
        layout.addWidget(self._create_video_card())
        self._batch_card = BatchQueueCard()
        self._batch_card.item_selected.connect(self._select_batch_item)
        self._batch_card.item_remove_requested.connect(self._remove_batch_item)
        self._batch_card.add_to_queue_requested.connect(self._add_current_to_queue)
        self._batch_card.clear_queue_requested.connect(self._clear_batch_queue)
        self._batch_card.hide()
        layout.addWidget(self._batch_card)
        layout.addWidget(self._create_subtitle_card())
        layout.addWidget(self._create_audio_card())
        layout.addWidget(self._create_watermark_card())
        layout.addWidget(self._create_preset_card())
        layout.addWidget(self._create_output_card())
        layout.addWidget(self._create_options_card())
        self._create_progress_bar()
        layout.addWidget(self._progress_bar)
        layout.addWidget(self._create_actions())
        layout.addWidget(self._create_log_section())

    def _create_header(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.addStretch()

        title = QLabel("HardSubForge")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {Color.PRIMARY};
            background-color: transparent;
        """)
        title_row.addWidget(title)
        title_row.addStretch()

        self._btn_theme = ModernButton("☀", variant=ButtonVariant.MINIMAL,
                                        color=Color.WARNING, hover_color=Color.TEXT_SECONDARY)
        self._btn_theme.setFixedSize(36, 36)
        self._btn_theme.setToolTip("Alternar tema claro/escuro")
        self._btn_theme.clicked.connect(self._toggle_theme)
        title_row.addWidget(self._btn_theme)

        layout.addLayout(title_row)

        version = QLabel(f"v{self.APP_VERSION} — Reencode com legendas hardcoded")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"""
            font-size: 12px;
            color: {Color.TEXT_MUTED};
            background-color: transparent;
        """)
        layout.addWidget(version)

        return widget

    def _create_status_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.SM)

        self._pill_ffmpeg = StatusPill("FFmpeg: --")
        layout.addWidget(self._pill_ffmpeg)

        gpu_text = "GPU: NVIDIA" if self.has_nvidia else "GPU: Nenhuma"
        gpu_color = Color.SUCCESS if self.has_nvidia else Color.WARNING
        gpu_bg = Color.SUCCESS_BG if self.has_nvidia else Color.WARNING_BG
        self._pill_gpu = StatusPill(gpu_text)
        self._pill_gpu.set_status(gpu_text, gpu_color, gpu_bg)
        layout.addWidget(self._pill_gpu)

        self._pill_encoder = StatusPill("Encoder: --")
        layout.addWidget(self._pill_encoder)

        layout.addStretch()
        return layout

    def _create_video_card(self) -> SectionCard:
        card = SectionCard("Arquivo de Entrada")
        self.drop_area = DropArea(parent_window=self)
        self.drop_area.files_dropped.connect(self._on_files_dropped)
        card.layout().addWidget(self.drop_area)
        return card

    def _create_subtitle_card(self) -> SectionCard:
        card = SectionCard("Legenda")
        card.setAcceptDrops(True)
        card.installEventFilter(self)
        self._subtitle_card = card

        externa_lbl = QLabel("Externa:")
        externa_lbl.setStyleSheet(f"color: {Color.TEXT_MUTED}; font-weight: bold; background-color: transparent; font-size: 12px;")
        card.layout().addWidget(externa_lbl)

        row = QHBoxLayout()
        row.setSpacing(Spacing.SM)

        self.lbl_subtitle = QLabel("Nenhuma detectada")
        self.lbl_subtitle.setStyleSheet(f"color: {Color.TEXT_MUTED}; background-color: transparent;")
        row.addWidget(self.lbl_subtitle, stretch=1)

        btn_select = ModernButton("Selecionar", variant=ButtonVariant.MINIMAL,
                                   color=Color.INFO, hover_color=Color.PRIMARY_HOVER)
        btn_select.clicked.connect(self._select_subtitle)
        row.addWidget(btn_select)

        btn_clear = ModernButton("Limpar", variant=ButtonVariant.MINIMAL,
                                  color=Color.TEXT_SECONDARY, hover_color=Color.BG_LIGHT)
        btn_clear.clicked.connect(self._clear_subtitle)
        row.addWidget(btn_clear)

        card.layout().addLayout(row)

        embutida_lbl = QLabel("Embutida (MKV):")
        embutida_lbl.setStyleSheet(f"color: {Color.TEXT_MUTED}; font-weight: bold; background-color: transparent; font-size: 12px; padding-top: 8px;")
        card.layout().addWidget(embutida_lbl)

        emb_row = QHBoxLayout()
        emb_row.setSpacing(Spacing.SM)
        self.combo_subtitle_embedded = QComboBox()
        self.combo_subtitle_embedded.setMinimumWidth(250)
        self.combo_subtitle_embedded.addItem("Nenhuma (nao usar legenda)", None)
        self.combo_subtitle_embedded.setEnabled(False)
        emb_row.addWidget(self.combo_subtitle_embedded, stretch=1)
        card.layout().addLayout(emb_row)

        self.chk_subtitle_burn = QCheckBox("Queimar legenda no video (burn-in)")
        self.chk_subtitle_burn.setChecked(False)
        self.chk_subtitle_burn.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-weight: bold; padding-top: 4px;")
        card.layout().addWidget(self.chk_subtitle_burn)

        return card

    def _create_audio_card(self) -> SectionCard:
        card = SectionCard("Audio")
        row = QHBoxLayout()
        row.setSpacing(Spacing.SM)

        self.lbl_audio = QLabel("Audio:")
        self.lbl_audio.setStyleSheet(f"color: {Color.TEXT_MUTED}; background-color: transparent;")
        row.addWidget(self.lbl_audio)

        self.combo_audio = QComboBox()
        self.combo_audio.setMinimumWidth(250)
        row.addWidget(self.combo_audio, stretch=1)

        card.layout().addLayout(row)
        return card

    def _create_watermark_card(self) -> SectionCard:
        card = SectionCard("Watermark / Texto Superior")

        text_row = QHBoxLayout()
        text_row.setSpacing(Spacing.SM)
        self.entry_watermark = QLineEdit()
        self.entry_watermark.setPlaceholderText("Digite o texto do watermark...")
        text_row.addWidget(self.entry_watermark)

        self.spin_watermark_size = QSpinBox()
        self.spin_watermark_size.setRange(10, 72)
        self.spin_watermark_size.setValue(22)
        self.spin_watermark_size.setPrefix("Tamanho: ")
        text_row.addWidget(self.spin_watermark_size)
        card.layout().addLayout(text_row)

        pos_row = QHBoxLayout()
        pos_row.setSpacing(Spacing.SM)
        pos_label = QLabel("Posicao:")
        pos_label.setStyleSheet(f"color: {Color.TEXT_MUTED}; background-color: transparent;")
        pos_row.addWidget(pos_label)
        self.combo_watermark_pos = QComboBox()
        self.combo_watermark_pos.addItems(["Topo", "Centro", "Rodape"])
        self.combo_watermark_pos.setCurrentText("Topo")
        pos_row.addWidget(self.combo_watermark_pos)
        pos_row.addStretch()

        btn_preview = ModernButton("Preview", variant=ButtonVariant.MINIMAL,
                                    color=Color.INFO, hover_color=Color.PRIMARY_HOVER)
        btn_preview.setFixedHeight(30)
        btn_preview.clicked.connect(self._generate_preview)
        pos_row.addWidget(btn_preview)

        card.layout().addLayout(pos_row)

        return card

    def _create_preset_card(self) -> SectionCard:
        card = SectionCard("Preset de Qualidade")

        row = QHBoxLayout()
        row.setSpacing(Spacing.SM)

        self.combo_preset = QComboBox()
        self.combo_preset.setMinimumWidth(200)
        self._load_presets()
        self.combo_preset.currentIndexChanged.connect(self._on_preset_changed)
        row.addWidget(self.combo_preset, stretch=1)

        btn_add = ModernButton("+", variant=ButtonVariant.SUCCESS)
        btn_add.setFixedSize(32, 32)
        btn_add.setToolTip("Criar novo Preset")
        btn_add.clicked.connect(self._add_preset)
        row.addWidget(btn_add)

        btn_del = ModernButton("-", variant=ButtonVariant.DANGER)
        btn_del.setFixedSize(32, 32)
        btn_del.setToolTip("Deletar Preset")
        btn_del.clicked.connect(self._delete_preset)
        row.addWidget(btn_del)

        card.layout().addLayout(row)

        bitrate_lbl = QLabel("Bitrate Medio (kbps):")
        bitrate_lbl.setStyleSheet(f"color: {Color.TEXT_MUTED}; font-weight: bold; background-color: transparent; font-size: 12px; padding-top: 8px;")
        card.layout().addWidget(bitrate_lbl)

        slider_row = QHBoxLayout()
        slider_row.setSpacing(Spacing.MD)

        self._slider_bitrate = QSlider(Qt.Orientation.Horizontal)
        self._slider_bitrate.setRange(500, 15000)
        self._slider_bitrate.setValue(4500)
        self._slider_bitrate.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider_bitrate.setTickInterval(2500)
        self._slider_bitrate.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {Color.BG_LIGHT};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {Color.PRIMARY};
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {Color.PRIMARY_HOVER};
            }}
            QSlider::sub-page:horizontal {{
                background: {Color.PRIMARY};
                border-radius: 3px;
            }}
        """)
        self._slider_bitrate.valueChanged.connect(self._on_bitrate_slider_changed)
        slider_row.addWidget(self._slider_bitrate, stretch=1)

        self._spin_bitrate = QSpinBox()
        self._spin_bitrate.setRange(500, 15000)
        self._spin_bitrate.setValue(4500)
        self._spin_bitrate.setSuffix(" kbps")
        self._spin_bitrate.setSingleStep(100)
        self._spin_bitrate.setFixedWidth(120)
        self._spin_bitrate.valueChanged.connect(self._on_bitrate_spin_changed)
        slider_row.addWidget(self._spin_bitrate)

        card.layout().addLayout(slider_row)

        self._lbl_bitrate_info = QLabel("")
        self._lbl_bitrate_info.setStyleSheet(f"color: {Color.TEXT_MUTED}; background-color: transparent; font-size: 11px;")
        card.layout().addWidget(self._lbl_bitrate_info)

        self._lbl_estimated_size = QLabel("")
        self._lbl_estimated_size.setStyleSheet(f"color: {Color.INFO}; background-color: transparent; font-size: 11px; font-weight: bold;")
        card.layout().addWidget(self._lbl_estimated_size)

        self._update_bitrate_info()
        return card

    def _create_output_card(self) -> SectionCard:
        card = SectionCard("Arquivo de Saida")

        path_row = QHBoxLayout()
        path_row.setSpacing(Spacing.SM)
        self.entry_output_path = QLineEdit()
        self.entry_output_path.setPlaceholderText("Pasta de saida (opcional)")
        path_row.addWidget(self.entry_output_path)

        btn_browse = ModernButton("📁", variant=ButtonVariant.MINIMAL,
                                   color=Color.INFO, hover_color=Color.PRIMARY_HOVER)
        btn_browse.setFixedSize(36, 36)
        btn_browse.setToolTip("Selecionar pasta de saida")
        btn_browse.clicked.connect(self._browse_output_path)
        path_row.addWidget(btn_browse)

        card.layout().addLayout(path_row)

        name_row = QHBoxLayout()
        name_row.setSpacing(Spacing.SM)
        name_label = QLabel("Nome:")
        name_label.setStyleSheet(f"color: {Color.TEXT_MUTED}; background-color: transparent;")
        name_row.addWidget(name_label)

        self.entry_output_name = QLineEdit()
        self.entry_output_name.setPlaceholderText("Nome do arquivo (opcional)")
        name_row.addWidget(self.entry_output_name, stretch=1)
        card.layout().addLayout(name_row)

        return card

    def _create_options_card(self) -> SectionCard:
        card = SectionCard("Opcoes")

        self.chk_hw_accel = QCheckBox("Usar aceleracao por hardware (NVIDIA NVENC)")
        self.chk_hw_accel.setChecked(self.has_nvidia)
        self.chk_hw_accel.setEnabled(self.has_nvidia)
        card.layout().addWidget(self.chk_hw_accel)

        self.chk_copy_audio = QCheckBox("Copiar audio sem reencode (mais rapido)")
        self.chk_copy_audio.setChecked(False)
        card.layout().addWidget(self.chk_copy_audio)

        self.chk_metadata = QCheckBox("Preservar metadados do video original")
        self.chk_metadata.setChecked(True)
        card.layout().addWidget(self.chk_metadata)

        return card

    def _create_progress_bar(self) -> None:
        self._progress_bar = QProgressBar()
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {Color.BORDER};
                border-radius: {Radius.MD}px;
                text-align: center;
                color: {Color.TEXT_PRIMARY};
                min-height: 26px;
                font-weight: bold;
                font-size: 12px;
                background-color: {Color.PROGRESS_BG};
            }}
            QProgressBar::chunk {{
                background-color: {Color.PROGRESS_CHUNK};
                border-radius: {Radius.MD - 1}px;
            }}
        """)

    def _create_actions(self) -> QWidget:
        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(Spacing.MD)

        self.btn_convert = ModernButton("INICIAR CONVERSAO", variant=ButtonVariant.SUCCESS)
        self.btn_convert.clicked.connect(self._start_conversion)
        self.btn_convert.setFixedHeight(46)
        btn_row.addWidget(self.btn_convert, stretch=1)

        self.btn_cancel = ModernButton("CANCELAR", variant=ButtonVariant.DANGER)
        self.btn_cancel.clicked.connect(self._cancel_conversion)
        self.btn_cancel.setFixedHeight(46)
        self.btn_cancel.setEnabled(False)
        btn_row.addWidget(self.btn_cancel, stretch=1)

        layout.addLayout(btn_row)
        return widget

    def _create_log_section(self) -> SectionCard:
        card = SectionCard("Log de Conversao")
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(160)
        self.txt_log.document().setMaximumBlockCount(1000)
        self.txt_log.setStyleSheet(f"""
            background-color: {Color.LOG_BG};
            color: {Color.LOG_TEXT};
            font-family: "Consolas", "Cascadia Code", monospace;
            font-size: 11px;
            border: 1px solid {Color.BORDER};
            border-radius: {Radius.MD}px;
        """)
        card.layout().addWidget(self.txt_log)
        return card

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _setup_tray_icon(self) -> None:
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = Path(__file__).parent.parent / "icon.ico"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        self.tray_icon.show()

    def _update_status_ui(self) -> None:
        if self.ffmpeg_wrapper.ffmpeg_path:
            self._pill_ffmpeg.set_status("FFmpeg: OK", Color.SUCCESS, Color.SUCCESS_BG)
            if self.chk_hw_accel.isChecked() and self.has_nvidia:
                self._pill_encoder.set_status("Encoder: NVENC", Color.INFO, Color.INFO_BG)
            else:
                self._pill_encoder.set_status("Encoder: CPU (libx264)", Color.TEXT_MUTED, Color.BG_MEDIUM)
        else:
            self._pill_ffmpeg.set_status("FFmpeg: NAO ENCONTRADO", Color.DANGER, Color.DANGER_BG)
            self._pill_encoder.set_status("Encoder: --", Color.TEXT_MUTED, Color.BG_MEDIUM)

    def _load_settings(self) -> None:
        watermark_text = self.config.get("last_watermark_text", "")
        self.entry_watermark.setText(watermark_text)
        self.spin_watermark_size.setValue(self.config.get("watermark_size", 22))

        pos_map = {"top": "Topo", "center": "Centro", "bottom": "Rodape"}
        self.combo_watermark_pos.setCurrentText(
            pos_map.get(self.config.get("watermark_position", "top"), "Topo"))

        self.chk_hw_accel.setChecked(self.config.get("use_hardware_accel", True))
        self.chk_copy_audio.setChecked(self.config.get("copy_audio", False))
        self.chk_metadata.setChecked(self.config.get("preserve_metadata", True))

        last_output = self.config.get("last_output_dir", "")
        if last_output:
            self.entry_output_path.setText(last_output)

        last_preset = self.config.get("last_preset", "Maxima Qualidade")
        idx = self.combo_preset.findText(last_preset)
        if idx >= 0:
            self.combo_preset.setCurrentIndex(idx)

        last_bitrate = self.config.get("last_bitrate", 4500)
        self._spin_bitrate.setValue(last_bitrate)
        self._update_bitrate_info()

        self._dark_theme = self.config.get("dark_theme", True)
        if not self._dark_theme:
            self._toggle_theme()

    def _save_settings(self) -> None:
        self.config.set("last_watermark_text", self.entry_watermark.text())
        self.config.set("watermark_size", self.spin_watermark_size.value())

        pos_map = {"Topo": "top", "Centro": "center", "Rodape": "bottom"}
        self.config.set("watermark_position", pos_map.get(self.combo_watermark_pos.currentText(), "top"))

        self.config.set("use_hardware_accel", self.chk_hw_accel.isChecked())
        self.config.set("copy_audio", self.chk_copy_audio.isChecked())
        self.config.set("preserve_metadata", self.chk_metadata.isChecked())
        self.config.set("last_preset", self.combo_preset.currentText())
        self.config.set("last_bitrate", self._spin_bitrate.value())

        if self.output_path:
            self.config.set("last_output_dir", self.output_path)
        if self.video_path:
            self.config.set("last_video_dir", str(Path(self.video_path).parent))

        self.config.save()

    def _load_presets(self) -> None:
        self.combo_preset.blockSignals(True)
        self.combo_preset.clear()
        for preset in StreamingPresets.get_all():
            self.combo_preset.addItem(f"🎬 {preset.name}", preset)
        for preset in self.config.get_custom_presets():
            self.combo_preset.addItem(f"⚙️ {preset.name}", preset)
        self.combo_preset.blockSignals(False)

    # ------------------------------------------------------------------
    # File Handling
    # ------------------------------------------------------------------

    @Slot(list)
    def _on_files_dropped(self, files: List[str]) -> None:
        if not files:
            return
        if len(files) == 1 and not self.batch_queue:
            self._load_video(files[0])
        else:
            for f in files:
                self._add_file_to_queue(f)
            self._refresh_batch_ui()
            self._batch_card.show()
            if not self._batch_processing:
                self._select_batch_item(len(self.batch_queue) - 1)

    @Slot()
    def _select_video_dialog(self) -> None:
        last_dir = self.config.get("last_video_dir", "")
        if not last_dir:
            last_dir = str(Path.home())

        paths, _ = QFileDialog.getOpenFileNames(
            self, "Selecione os arquivos de video",
            last_dir,
            "Videos (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm);;Todos os arquivos (*.*)"
        )
        if paths:
            if len(paths) == 1 and not self.batch_queue:
                self._load_video(paths[0])
            else:
                for f in paths:
                    self._add_file_to_queue(f)
                self._refresh_batch_ui()
                self._batch_card.show()
                if not self._batch_processing:
                    self._select_batch_item(len(self.batch_queue) - 1)

    def _load_video(self, path: str) -> None:
        self.video_path = path
        self.drop_area.setText(f"📁 {Path(path).name}")
        self.drop_area.setStyleSheet(DropArea.ACTIVE_STYLE)

        self._detect_subtitle(path)
        self._probe_audio_and_subtitles(path)
        QTimer.singleShot(500, self._update_estimated_size)

        if not self.entry_output_name.text():
            self.entry_output_name.setText(Path(path).stem + "_converted")

        if not self.output_path:
            self.entry_output_path.setText(str(Path(path).parent))

    def _detect_subtitle(self, video_path: str) -> None:
        video_dir = Path(video_path).parent
        video_name = Path(video_path).stem

        self.combo_subtitle_embedded.setCurrentIndex(0)

        for ext in ['.srt', '.ass', '.ssa']:
            sub_path = video_dir / (video_name + ext)
            if sub_path.exists():
                self.subtitle_path = str(sub_path)
                self.lbl_subtitle.setText(f"Externa: {sub_path.name}")
                self.lbl_subtitle.setStyleSheet(f"color: {Color.SUCCESS}; background-color: transparent;")
                return

        self.subtitle_path = ""
        self.lbl_subtitle.setText("Externa: Nenhuma detectada")
        self.lbl_subtitle.setStyleSheet(f"color: {Color.TEXT_MUTED}; background-color: transparent;")

    @Slot()
    def _select_subtitle(self) -> None:
        if not self.video_path:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecione a Legenda",
            str(Path(self.video_path).parent),
            "Legendas (*.srt *.ass *.ssa);;Todos os arquivos (*.*)"
        )
        if path:
            self.subtitle_path = path
            self.lbl_subtitle.setText(f"Externa: {Path(path).name}")
            self.lbl_subtitle.setStyleSheet(f"color: {Color.SUCCESS}; background-color: transparent;")

    @Slot()
    def _clear_subtitle(self) -> None:
        self.subtitle_path = ""
        self.lbl_subtitle.setText("Legenda: Nenhuma selecionada")
        self.lbl_subtitle.setStyleSheet(f"color: {Color.TEXT_MUTED}; background-color: transparent;")
        self.combo_subtitle_embedded.setCurrentIndex(0)

    @Slot()
    def _browse_output_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saida")
        if path:
            self.entry_output_path.setText(path)

    # ------------------------------------------------------------------
    # Batch Queue
    # ------------------------------------------------------------------

    def _auto_detect_subtitle_for(self, video_path: str) -> str:
        video_dir = Path(video_path).parent
        video_name = Path(video_path).stem
        for ext in ['.srt', '.ass', '.ssa']:
            sub_path = video_dir / (video_name + ext)
            if sub_path.exists():
                return str(sub_path)
        return ""

    def _add_file_to_queue(self, file_path: str) -> BatchItem:
        item = BatchItem(path=file_path)
        sub = self._auto_detect_subtitle_for(file_path)
        if sub:
            item.detected_external = sub
            item.subtitle_path = sub
        item.output_name = Path(file_path).stem + "_converted"
        self.batch_queue.append(item)
        return item

    def _add_current_to_queue(self) -> None:
        if not self.video_path:
            QMessageBox.warning(self, "Aviso", "Carregue um video antes de adicionar a fila.")
            return
        existing = next((i for i in self.batch_queue if i.path == self.video_path), None)
        if existing:
            self._sync_batch_item_from_ui()
            self._refresh_batch_ui()
            return
        item = BatchItem(path=self.video_path)
        item.subtitle_path = self.subtitle_path
        item.subtitle_stream_index = self.combo_subtitle_embedded.currentData()
        item.subtitle_burn = self.chk_subtitle_burn.isChecked()
        item.audio_track_index = self.combo_audio.currentData()
        item.output_name = self.entry_output_name.text() or (Path(self.video_path).stem + "_converted")
        sub = self._auto_detect_subtitle_for(self.video_path)
        item.detected_external = sub
        self.batch_queue.append(item)
        self._refresh_batch_ui()
        self._batch_card.show()
        self._log(f"Adicionado a fila: {item.filename}")

    def _sync_batch_item_from_ui(self) -> None:
        if self._batch_selected_index < 0 or self._batch_selected_index >= len(self.batch_queue):
            return
        item = self.batch_queue[self._batch_selected_index]
        item.subtitle_path = self.subtitle_path
        item.subtitle_stream_index = self.combo_subtitle_embedded.currentData()
        item.subtitle_burn = self.chk_subtitle_burn.isChecked()
        item.audio_track_index = self.combo_audio.currentData()
        item.output_name = self.entry_output_name.text() or (Path(item.path).stem + "_converted")

    @Slot(int)
    def _select_batch_item(self, index: int) -> None:
        if index < 0 or index >= len(self.batch_queue):
            return
        self._sync_batch_item_from_ui()
        self._batch_selected_index = index
        item = self.batch_queue[index]
        self.video_path = item.path
        self.subtitle_path = item.subtitle_path
        self.drop_area.setText(f"📁 {Path(item.path).name}")
        self.drop_area.setStyleSheet(DropArea.ACTIVE_STYLE)
        if item.subtitle_path:
            self.lbl_subtitle.setText(f"Externa: {Path(item.subtitle_path).name}")
            self.lbl_subtitle.setStyleSheet(f"color: {Color.SUCCESS}; background-color: transparent;")
        else:
            self.lbl_subtitle.setText("Externa: Nenhuma detectada")
            self.lbl_subtitle.setStyleSheet(f"color: {Color.TEXT_MUTED}; background-color: transparent;")
        self.chk_subtitle_burn.setChecked(item.subtitle_burn)
        self.entry_output_name.setText(item.output_name)
        self._probe_audio_and_subtitles(item.path)

    @Slot(int)
    def _remove_batch_item(self, index: int) -> None:
        if self._batch_processing:
            return
        if 0 <= index < len(self.batch_queue):
            removed = self.batch_queue.pop(index)
            if self._batch_selected_index == index:
                self._batch_selected_index = -1
            elif self._batch_selected_index > index:
                self._batch_selected_index -= 1
            self._refresh_batch_ui()
            if not self.batch_queue:
                self._batch_card.hide()
            else:
                new_idx = min(self._batch_selected_index, len(self.batch_queue) - 1)
                if new_idx >= 0:
                    self._select_batch_item(new_idx)

    @Slot()
    def _clear_batch_queue(self) -> None:
        if self._batch_processing:
            QMessageBox.warning(self, "Aviso", "Nao e possivel limpar a fila durante o processamento.")
            return
        reply = QMessageBox.question(
            self, "Limpar Fila",
            f"Remover todos os {len(self.batch_queue)} arquivos da fila?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.batch_queue.clear()
            self._batch_selected_index = -1
            self._batch_card.hide()
            self._refresh_batch_ui()

    def _refresh_batch_ui(self) -> None:
        if self.batch_queue:
            self._batch_card.set_items(self.batch_queue)
            if self._batch_selected_index >= 0:
                self._batch_card.select_row(self._batch_selected_index)
            if not self._batch_processing:
                self.btn_convert.setText(f"INICIAR LOTE ({len(self.batch_queue)})")
        else:
            self.btn_convert.setText("INICIAR CONVERSAO")

    # ------------------------------------------------------------------
    # Audio Probe
    # ------------------------------------------------------------------

    def _probe_audio_and_subtitles(self, video_path: str) -> None:
        self._cleanup_probe()
        self._probe_generation += 1
        gen = self._probe_generation

        self._probe_thread = QThread()
        self._probe_worker = ProbeWorker(self.ffmpeg_wrapper, video_path)
        self._probe_worker._generation = gen
        self._probe_worker.moveToThread(self._probe_thread)

        self._probe_thread.started.connect(self._probe_worker.run)
        self._probe_worker.finished_signal.connect(self._on_audio_probed)
        self._probe_worker.finished_signal.connect(self._probe_thread.quit)
        self._probe_worker.finished_signal.connect(self._probe_worker.deleteLater)
        self._probe_thread.finished.connect(self._probe_thread.deleteLater)
        self._probe_thread.finished.connect(self._on_probe_thread_done)

        self._probe_thread.start()

    def _cleanup_probe(self) -> None:
        if self._probe_thread and self._probe_thread.isRunning():
            self._probe_thread.quit()
            self._probe_thread.wait(3000)

    @Slot()
    def _on_probe_thread_done(self) -> None:
        self._probe_thread = None
        self._probe_worker = None

    @Slot(dict)
    def _on_audio_probed(self, streams: dict) -> None:
        worker = self.sender()
        if hasattr(worker, '_generation') and worker._generation != self._probe_generation:
            return

        audio = streams.get("audio", [])
        subtitles = streams.get("subtitles", [])

        self.combo_audio.clear()
        self.combo_audio.addItem("Padrao (Todas as faixas)", None)

        if audio:
            self.lbl_audio.setText("Audio:")
            self.combo_audio.setEnabled(True)
            for s in audio:
                self.combo_audio.addItem(s['title'], s['index'])
        else:
            self.lbl_audio.setText("Audio: Nenhuma faixa detectada")
            self.combo_audio.setEnabled(False)

        self.combo_subtitle_embedded.clear()
        self.combo_subtitle_embedded.addItem("Nenhuma (nao usar legenda)", None)

        text_subs = [s for s in subtitles if is_text_subtitle(s.get('codec', ''))]
        unsupported = [s for s in subtitles if not is_text_subtitle(s.get('codec', ''))]

        if text_subs:
            self.combo_subtitle_embedded.setEnabled(True)
            for s in text_subs:
                self.combo_subtitle_embedded.addItem(s['title'], s['index'])
        else:
            self.combo_subtitle_embedded.setEnabled(False)

        if self._batch_selected_index >= 0 and self._batch_selected_index < len(self.batch_queue):
            item = self.batch_queue[self._batch_selected_index]
            if item.subtitle_stream_index is not None:
                idx = self.combo_subtitle_embedded.findData(item.subtitle_stream_index)
                if idx >= 0:
                    self.combo_subtitle_embedded.setCurrentIndex(idx)
            if item.audio_track_index is not None:
                idx = self.combo_audio.findData(item.audio_track_index)
                if idx >= 0:
                    self.combo_audio.setCurrentIndex(idx)

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------

    @Slot()
    def _add_preset(self) -> None:
        dialog = AddPresetDialog(self)
        if dialog.exec() == AddPresetDialog.DialogCode.Accepted:
            preset = dialog.get_preset_data()
            if preset:
                self.config.add_custom_preset(preset)
                self._load_presets()
                self.combo_preset.setCurrentText(f"⚙️ {preset.name}")
                QMessageBox.information(self, "Sucesso", f"Preset '{preset.name}' salvo!")

    @Slot()
    def _delete_preset(self) -> None:
        current_text = self.combo_preset.currentText()
        if not current_text.startswith("⚙️"):
            QMessageBox.information(self, "Info", "Apenas presets customizados podem ser deletados.")
            return

        name = current_text[2:]
        reply = QMessageBox.question(
            self, "Deletar Preset",
            f"Deseja realmente deletar o preset '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config.remove_custom_preset(name)
            self._load_presets()
            QMessageBox.information(self, "Sucesso", f"Preset '{name}' deletado!")

    # ------------------------------------------------------------------
    # Bitrate & Estimativa
    # ------------------------------------------------------------------

    @Slot(int)
    def _on_bitrate_slider_changed(self, value: int) -> None:
        self._spin_bitrate.blockSignals(True)
        self._spin_bitrate.setValue(value)
        self._spin_bitrate.blockSignals(False)
        self._update_estimated_size()

    @Slot(int)
    def _on_bitrate_spin_changed(self, value: int) -> None:
        self._slider_bitrate.blockSignals(True)
        self._slider_bitrate.setValue(value)
        self._slider_bitrate.blockSignals(False)
        self._update_estimated_size()

    @Slot(int)
    def _on_preset_changed(self, index: int) -> None:
        if index < 0:
            return
        preset_data = self.combo_preset.currentData()
        if preset_data:
            kbps = int(preset_data.bitrate.replace("k", ""))
            self._slider_bitrate.setValue(kbps)
            preset_name = self.combo_preset.currentText()
            self._lbl_bitrate_info.setText(f"Bitrate recomendado pelo preset: {preset_data.bitrate}")
            self._update_estimated_size()

    def _update_bitrate_info(self) -> None:
        preset_data = self.combo_preset.currentData()
        if preset_data:
            self._lbl_bitrate_info.setText(f"Bitrate recomendado pelo preset: {preset_data.bitrate}")
            self._update_estimated_size()

    def _update_estimated_size(self) -> None:
        if not self.video_path or not self.ffmpeg_wrapper.ffprobe_path:
            self._lbl_estimated_size.setText("")
            return

        bitrate_kbps = self._spin_bitrate.value()
        duration = self.ffmpeg_wrapper.get_duration(self.video_path)
        if duration <= 0:
            self._lbl_estimated_size.setText("")
            return

        size_mb = (bitrate_kbps * duration) / 8 / 1024
        audio_kbps = 128
        audio_mb = (audio_kbps * duration) / 8 / 1024
        total_mb = size_mb + audio_mb
        self._lbl_estimated_size.setText(
            f"Tamanho estimado: ~{total_mb:.0f} MB  ({duration:.0f}s @ {bitrate_kbps}kbps)")

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    @Slot()
    def _start_conversion(self) -> None:
        if not self.ffmpeg_wrapper.ffmpeg_path:
            QMessageBox.warning(self, "Aviso", "FFmpeg nao encontrado. Configure o caminho nas configuracoes.")
            return
        if self.batch_queue:
            self._sync_batch_item_from_ui()
            self._start_batch()
        elif self.video_path:
            self._start_single()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo de video primeiro.")

    def _start_single(self) -> None:
        output_path = self.entry_output_path.text() or str(Path(self.video_path).parent)
        output_name = self.entry_output_name.text() or (Path(self.video_path).stem + "_converted")
        output_full = str(Path(output_path) / f"{output_name}.mp4")
        options = self._build_options(self.video_path, output_full,
                                       self.subtitle_path,
                                       self.combo_subtitle_embedded.currentData(),
                                       self.chk_subtitle_burn.isChecked(),
                                       self.combo_audio.currentData())
        self._save_settings()
        self._start_worker(options)

    def _build_options(self, input_path: str, output_path: str,
                       subtitle_path: str, subtitle_stream_index, subtitle_burn: bool,
                       audio_track_index) -> ConversionOptions:
        preset_data = self.combo_preset.currentData()
        pos_map = {"Topo": "top", "Centro": "center", "Rodape": "bottom"}
        return ConversionOptions(
            input_path=input_path,
            output_path=output_path,
            preset=preset_data,
            subtitle_path=subtitle_path,
            subtitle_stream_index=subtitle_stream_index,
            subtitle_burn=subtitle_burn,
            custom_bitrate=f"{self._spin_bitrate.value()}k",
            watermark_text=self.entry_watermark.text(),
            watermark_position=pos_map.get(self.combo_watermark_pos.currentText(), "top"),
            watermark_size=self.spin_watermark_size.value(),
            audio_track_index=audio_track_index,
            use_hardware_accel=self.chk_hw_accel.isChecked(),
            copy_audio=self.chk_copy_audio.isChecked(),
            preserve_metadata=self.chk_metadata.isChecked()
        )

    def _start_worker(self, options: ConversionOptions) -> None:
        self.btn_convert.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self._progress_bar.setValue(0)
        self._worker_thread = QThread()
        self._worker = ConversionWorker(options, self.ffmpeg_wrapper)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.progress_signal.connect(self._progress_bar.setValue)
        self._worker.log_signal.connect(self._log)
        self._worker.finished_signal.connect(self._on_conversion_finished)
        self._worker.finished_signal.connect(self._worker_thread.quit)
        self._worker.finished_signal.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)
        self._worker_thread.finished.connect(self._on_thread_done)
        self._worker_thread.start()

    def _start_batch(self) -> None:
        self._batch_processing = True
        self._batch_completed = 0
        self._batch_errors = 0
        self._save_settings()
        self._log(f"Iniciando lote com {len(self.batch_queue)} arquivo(s)...")
        self._process_next_batch()

    def _process_next_batch(self) -> None:
        for i, item in enumerate(self.batch_queue):
            if item.status == "pending":
                self._batch_selected_index = i
                item.status = "converting"
                self._batch_card.update_item_status(i, "converting")
                self._batch_card.select_row(i)
                self._log(f"[{i + 1}/{len(self.batch_queue)}] Iniciando: {item.filename}")
                self.btn_convert.setText(f"Processando {i + 1}/{len(self.batch_queue)}...")
                self.btn_convert.setEnabled(False)
                self.btn_cancel.setEnabled(True)

                output_dir = self.entry_output_path.text() or str(Path(item.path).parent)
                output_name = item.output_name or (Path(item.path).stem + "_converted")
                output_full = self._unique_output_path(output_dir, output_name)

                if not item.subtitle_path:
                    sub = self._auto_detect_subtitle_for(item.path)
                    if sub:
                        item.subtitle_path = sub

                options = self._build_options(item.path, output_full,
                                               item.subtitle_path,
                                               item.subtitle_stream_index,
                                               item.subtitle_burn,
                                               item.audio_track_index)
                item.output_path = output_full
                self._start_worker(options)
                return

        self._finish_batch()

    def _unique_output_path(self, directory: str, name: str) -> str:
        base = Path(directory) / f"{name}.mp4"
        if not base.exists():
            return str(base)
        for n in range(2, 100):
            alt = Path(directory) / f"{name}_{n}.mp4"
            if not alt.exists():
                return str(alt)
        return str(base)

    @Slot()
    def _on_thread_done(self) -> None:
        if self.sender() is self._worker_thread:
            self._worker_thread = None
            self._worker = None

    @Slot()
    def _cancel_conversion(self) -> None:
        if not self._worker:
            return
        if self._batch_processing:
            remaining = sum(1 for i in self.batch_queue if i.status == "pending")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setWindowTitle("Cancelar Lote")
            msg.setText(f"Deseja cancelar o processamento?")
            msg.setInformativeText(f"Arquivos restantes: {remaining}")
            btn_current = msg.addButton("Cancelar este video", QMessageBox.ButtonRole.DestructiveRole)
            btn_all = msg.addButton("Cancelar lote inteiro", QMessageBox.ButtonRole.DestructiveRole)
            btn_no = msg.addButton("Continuar", QMessageBox.ButtonRole.AcceptRole)
            msg.exec()
            clicked = msg.clickedButton()
            if clicked == btn_no:
                return
            if clicked == btn_all:
                for i, item in enumerate(self.batch_queue):
                    if item.status == "pending":
                        item.status = "error"
                        item.error_msg = "cancelado"
                        self._batch_card.update_item_status(i, "error")
                self._log("Lote cancelado pelo usuario.")
            if clicked == btn_current or clicked == btn_all:
                self._log("Cancelando conversao...")
                self._worker.stop()
            if clicked == btn_current:
                return
        else:
            self._log("Cancelando conversao...")
            self._worker.stop()

    @Slot(int, str)
    def _on_conversion_finished(self, returncode: int, output_path: str) -> None:
        if self._batch_processing:
            idx = self._batch_selected_index
            if 0 <= idx < len(self.batch_queue):
                item = self.batch_queue[idx]
                if returncode == 0:
                    item.status = "done"
                    self._batch_completed += 1
                    self._log(f"✅ [{idx + 1}/{len(self.batch_queue)}] Concluido: {item.filename}")
                else:
                    item.status = "error"
                    item.error_msg = f"codigo {returncode}"
                    self._batch_errors += 1
                    self._log(f"❌ [{idx + 1}/{len(self.batch_queue)}] Erro: {item.filename} (codigo {returncode})")
                self._batch_card.update_item_status(idx, item.status)
            self._process_next_batch()
        else:
            self.btn_convert.setEnabled(True)
            self.btn_cancel.setEnabled(False)
            if returncode == 0:
                self._progress_bar.setValue(100)
                self._log(f"✅ Conversao concluida com sucesso!")
                self._log(f"📁 Arquivo salvo: {output_path}")
                reply = QMessageBox.question(
                    self, "Conversao Concluida",
                    f"Conversao finalizada!\n\nArquivo: {Path(output_path).name}\n\nDeseja abrir a pasta do arquivo?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(output_path).parent)))
                if self.tray_icon.isVisible():
                    self.tray_icon.showMessage(
                        "HardSubForge",
                        "Conversao finalizada!",
                        QSystemTrayIcon.MessageIcon.Information,
                        3000
                    )
            else:
                self._log(f"❌ Erro na conversao (codigo {returncode})")
                QMessageBox.critical(self, "Erro", f"Erro na conversao (codigo {returncode})")

    def _finish_batch(self) -> None:
        self._batch_processing = False
        total = len(self.batch_queue)
        self.btn_convert.setText("INICIAR CONVERSAO")
        self.btn_convert.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        summary = f"Lote concluido: {self._batch_completed} ok, {self._batch_errors} erro(s) de {total}"
        self._log(f"📦 {summary}")
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                "HardSubForge",
                summary,
                QSystemTrayIcon.MessageIcon.Information,
                5000
            )
        if total > 1:
            first_output = next((i.output_path for i in self.batch_queue if i.status == "done"), "")
            if first_output:
                reply = QMessageBox.question(
                    self, "Lote Concluido",
                    f"{summary}\n\nDeseja abrir a pasta de saida?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(first_output).parent)))

    @Slot(str)
    def _log(self, message: str) -> None:
        self.txt_log.append(message)
        self.txt_log.verticalScrollBar().setValue(
            self.txt_log.verticalScrollBar().maximum())

    # ------------------------------------------------------------------
    # FFmpeg Setup
    # ------------------------------------------------------------------

    def _show_ffmpeg_warning(self) -> None:
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("FFmpeg Nao Encontrado")
        msg.setText("O FFmpeg e necessario para a conversao de videos.")
        msg.setInformativeText(
            "Voce pode baixa-lo automaticamente (apenas Windows) ou seleciona-lo manualmente.")

        btn_dl = msg.addButton("Baixar Automaticamente", QMessageBox.ButtonRole.ActionRole)
        btn_man = msg.addButton("Selecionar Manualmente", QMessageBox.ButtonRole.ActionRole)
        msg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        clicked = msg.clickedButton()
        if clicked == btn_dl:
            if platform.system() == "Windows":
                self._download_ffmpeg_windows()
            else:
                QMessageBox.information(
                    self, "Info", "Download automatico disponivel apenas para Windows.")
        elif clicked == btn_man:
            self._select_ffmpeg_manual()

    def _download_ffmpeg_windows(self) -> None:
        pass

    @Slot()
    def _select_ffmpeg_manual(self) -> None:
        if platform.system() == "Windows":
            filtro = "Executaveis (*.exe);;Todos os arquivos (*.*)"
        else:
            filtro = "Todos os arquivos (*.*)"

        path, _ = QFileDialog.getOpenFileName(
            self, "Selecione o executavel do FFmpeg", "", filtro)

        if path and Path(path).exists():
            self.config.set("ffmpeg_path", path)
            self.config.save()
            self.ffmpeg_wrapper = FFmpegWrapper(path)
            self._update_status_ui()
            QMessageBox.information(self, "Sucesso", "FFmpeg configurado com sucesso!")

    # ------------------------------------------------------------------
    # Autoscroll & Drag & Drop
    # ------------------------------------------------------------------

    def eventFilter(self, obj, event) -> bool:
        if self._subtitle_card and obj == self._subtitle_card:
            return self._handle_subtitle_drop(obj, event)
        if self._scroll_area and obj == self._scroll_area.viewport():
            return self._handle_autoscroll(event)
        return super().eventFilter(obj, event)

    def _handle_subtitle_drop(self, obj, event) -> bool:
        sub_exts = ('.srt', '.ass', '.ssa')
        if event.type() == event.Type.DragEnter:
            if event.mimeData().hasUrls():
                for url in event.mimeData().urls():
                    if url.toLocalFile().lower().endswith(sub_exts):
                        event.accept()
                        self._subtitle_card.setStyleSheet(
                            self._subtitle_card.styleSheet().replace(Color.BORDER, Color.BORDER_FOCUS))
                        return True
            event.ignore()
            return True

        if event.type() == event.Type.DragLeave:
            self._subtitle_card.setStyleSheet(
                self._subtitle_card.styleSheet().replace(Color.BORDER_FOCUS, Color.BORDER))
            return True

        if event.type() == event.Type.Drop:
            self._subtitle_card.setStyleSheet(
                self._subtitle_card.styleSheet().replace(Color.BORDER_FOCUS, Color.BORDER))
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path.lower().endswith(sub_exts):
                    self.subtitle_path = path
                    self.lbl_subtitle.setText(f"Externa: {Path(path).name}")
                    self.lbl_subtitle.setStyleSheet(f"color: {Color.SUCCESS}; background-color: transparent;")
                    self._log(f"Legenda carregada: {Path(path).name}")
                    event.accept()
                    return True
            return True

        return False

    def _handle_autoscroll(self, event) -> bool:
        if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.MiddleButton:
            self._autoscroll_active = True
            self._autoscroll_start = event.globalPosition().toPoint()
            self._autoscroll_initial = self._scroll_area.verticalScrollBar().value()
            self._scroll_area.viewport().setCursor(Qt.CursorShape.SizeVerCursor)
            return True

        if self._autoscroll_active and event.type() == event.Type.MouseMove:
            delta = self._autoscroll_start.y() - event.globalPosition().toPoint().y()
            self._scroll_area.verticalScrollBar().setValue(self._autoscroll_initial + delta)
            return True

        if self._autoscroll_active and event.type() == event.Type.MouseButtonRelease:
            self._autoscroll_active = False
            self._scroll_area.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            return True

        return False

    @Slot()
    def _toggle_theme(self) -> None:
        self._dark_theme = not self._dark_theme
        app = QApplication.instance()
        if self._dark_theme:
            apply_dark_theme(app)
            self._btn_theme.setText("☀")
        else:
            apply_light_theme(app)
            self._btn_theme.setText("🌙")
        self.config.set("dark_theme", self._dark_theme)
        self.config.save()

    @Slot()
    def _generate_preview(self) -> None:
        if not self.video_path:
            QMessageBox.warning(self, "Aviso", "Selecione um video primeiro.")
            return
        if not self.ffmpeg_wrapper.ffmpeg_path:
            QMessageBox.warning(self, "Aviso", "FFmpeg nao encontrado.")
            return

        import tempfile
        preview_path = Path(tempfile.gettempdir()) / "hardsubforge_preview.jpg"

        preset_data = self.combo_preset.currentData()
        pos_map = {"Topo": "top", "Centro": "center", "Rodape": "bottom"}

        options = ConversionOptions(
            input_path=self.video_path,
            output_path="",
            preset=preset_data,
            subtitle_path=self.subtitle_path,
            subtitle_stream_index=self.combo_subtitle_embedded.currentData(),
            subtitle_burn=self.chk_subtitle_burn.isChecked(),
            custom_bitrate=f"{self._spin_bitrate.value()}k",
            watermark_text=self.entry_watermark.text(),
            watermark_position=pos_map.get(self.combo_watermark_pos.currentText(), "top"),
            watermark_size=self.spin_watermark_size.value(),
        )

        duration = self.ffmpeg_wrapper.get_duration(self.video_path)
        seek_time = min(duration * 0.15, 30) if duration > 0 else 10

        self._log(f"Gerando preview em {seek_time:.0f}s...")
        success = self.ffmpeg_wrapper.generate_preview(options, str(preview_path), seek_time)

        if success and preview_path.exists():
            pixmap = QPixmap(str(preview_path))
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(640, Qt.TransformationMode.SmoothTransformation)
                dialog = QDialog(self)
                dialog.setWindowTitle("Preview — Legenda & Watermark")
                layout = QVBoxLayout(dialog)
                lbl = QLabel()
                lbl.setPixmap(scaled)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(lbl)
                close_btn = QPushButton("Fechar")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                self._log("Preview gerado com sucesso!")
                dialog.exec()
            else:
                self._log("Erro: nao foi possivel carregar o preview.")
        else:
            self._log("Erro ao gerar preview. Verifique se o FFmpeg esta funcionando.")
