"""Gerenciador de temas e estilos globais."""

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from ui.styles import Color, Spacing, Radius


def apply_dark_theme(app: QApplication) -> None:
    """Aplica o tema escuro moderno em toda a aplicacao."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(Color.BG_DARKEST))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(Color.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(Color.BG_DARK))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Color.BG_MEDIUM))
    palette.setColor(QPalette.ColorRole.Text, QColor(Color.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(Color.BG_MEDIUM))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(Color.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(Color.PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Color.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Color.BG_DARK))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Color.TEXT_PRIMARY))
    app.setPalette(palette)

    app.setStyleSheet(global_stylesheet())


def global_stylesheet() -> str:
    """Retorna a folha de estilos global."""
    return f"""
        * {{
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 13px;
        }}

        QWidget {{
            color: {Color.TEXT_PRIMARY};
            background-color: {Color.BG_DARKEST};
        }}

        QToolTip {{
            background-color: {Color.BG_DARK};
            color: {Color.TEXT_PRIMARY};
            border: 1px solid {Color.BORDER};
            padding: {Spacing.XS}px {Spacing.SM}px;
            border-radius: {Radius.MD}px;
        }}

        QLineEdit {{
            background-color: {Color.BG_DARK};
            color: {Color.TEXT_PRIMARY};
            border: 1px solid {Color.BORDER};
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM + 2}px {Spacing.MD}px;
            selection-background-color: {Color.PRIMARY};
        }}
        QLineEdit:focus {{
            border-color: {Color.BORDER_FOCUS};
        }}
        QLineEdit:disabled {{
            color: {Color.TEXT_MUTED};
            background-color: {Color.BG_MEDIUM};
        }}

        QComboBox {{
            background-color: {Color.BG_DARK};
            color: {Color.TEXT_PRIMARY};
            border: 1px solid {Color.BORDER};
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
        }}
        QComboBox:focus {{
            border-color: {Color.BORDER_FOCUS};
        }}
        QComboBox:disabled {{
            color: {Color.TEXT_MUTED};
            background-color: {Color.BG_MEDIUM};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: {Spacing.SM}px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {Color.BG_DARK};
            color: {Color.TEXT_PRIMARY};
            border: 1px solid {Color.BORDER};
            selection-background-color: {Color.PRIMARY};
            selection-color: {Color.TEXT_PRIMARY};
            outline: none;
        }}

        QCheckBox {{
            color: {Color.TEXT_SECONDARY};
            spacing: {Spacing.SM}px;
            background-color: transparent;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {Color.BORDER};
            border-radius: {Radius.SM}px;
            background-color: {Color.BG_DARK};
        }}
        QCheckBox::indicator:checked {{
            background-color: {Color.PRIMARY};
            border-color: {Color.PRIMARY};
        }}
        QCheckBox::indicator:hover {{
            border-color: {Color.BORDER_HOVER};
        }}

        QSpinBox {{
            background-color: {Color.BG_DARK};
            color: {Color.TEXT_PRIMARY};
            border: 1px solid {Color.BORDER};
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
        }}
        QSpinBox:focus {{
            border-color: {Color.BORDER_FOCUS};
        }}

        QTextEdit {{
            background-color: {Color.LOG_BG};
            color: {Color.LOG_TEXT};
            border: 1px solid {Color.BORDER};
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px;
            font-family: "Consolas", "Cascadia Code", monospace;
            font-size: 11px;
        }}

        QProgressBar {{
            background-color: {Color.PROGRESS_BG};
            color: {Color.TEXT_PRIMARY};
            border: 1px solid {Color.BORDER};
            border-radius: {Radius.MD}px;
            text-align: center;
            min-height: 24px;
            font-weight: bold;
            font-size: 12px;
        }}
        QProgressBar::chunk {{
            background-color: {Color.PROGRESS_CHUNK};
            border-radius: {Radius.MD - 1}px;
        }}

        QScrollBar:vertical {{
            background-color: transparent;
            width: 8px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background-color: {Color.BG_LIGHT};
            border-radius: {Radius.PILL}px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {Color.TEXT_MUTED};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QScrollBar:horizontal {{
            background-color: transparent;
            height: 8px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {Color.BG_LIGHT};
            border-radius: {Radius.PILL}px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {Color.TEXT_MUTED};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}

        QMessageBox {{
            background-color: {Color.BG_DARK};
        }}
        QMessageBox QLabel {{
            color: {Color.TEXT_PRIMARY};
        }}

        QMenu {{
            background-color: {Color.BG_DARK};
            color: {Color.TEXT_PRIMARY};
            border: 1px solid {Color.BORDER};
            border-radius: {Radius.MD}px;
            padding: {Spacing.XS}px;
        }}
        QMenu::item {{
            padding: {Spacing.SM}px {Spacing.XL}px;
            border-radius: {Radius.SM}px;
        }}
        QMenu::item:selected {{
            background-color: {Color.PRIMARY};
        }}
    """


def card_widget_style() -> str:
    """Estilo para widget tipo card."""
    return f"""
        background-color: {Color.BG_CARD};
        border: 1px solid {Color.BORDER};
        border-radius: {Radius.LG}px;
    """


def section_label_style() -> str:
    """Estilo para labels de secao."""
    return f"""
        font-size: 13px;
        font-weight: bold;
        color: {Color.TEXT_SECONDARY};
        padding-bottom: {Spacing.XS}px;
        background-color: transparent;
    """


def title_label_style() -> str:
    """Estilo para o titulo principal."""
    return f"""
        font-size: 28px;
        font-weight: bold;
        color: {Color.PRIMARY};
        background-color: transparent;
    """


def subtitle_label_style() -> str:
    """Estilo para subtitulos."""
    return f"""
        font-size: 12px;
        color: {Color.TEXT_MUTED};
        background-color: transparent;
    """


def apply_light_theme(app: QApplication) -> None:
    """Aplica o tema claro."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#F0F2F5"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1A1A2E"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#E8EAED"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1A1A2E"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1A1A2E"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1F6FEB"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#1A1A2E"))
    app.setPalette(palette)

    app.setStyleSheet(f"""
        * {{
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 13px;
        }}

        QWidget {{
            color: #1A1A2E;
            background-color: #F0F2F5;
        }}

        QToolTip {{
            background-color: #FFFFFF;
            color: #1A1A2E;
            border: 1px solid #D0D5DD;
            padding: {Spacing.XS}px {Spacing.SM}px;
            border-radius: {Radius.MD}px;
        }}

        QLineEdit {{
            background-color: #FFFFFF;
            color: #1A1A2E;
            border: 1px solid #D0D5DD;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM + 2}px {Spacing.MD}px;
            selection-background-color: #1F6FEB;
        }}
        QLineEdit:focus {{
            border-color: #1F6FEB;
        }}
        QLineEdit:disabled {{
            color: #999;
            background-color: #F0F2F5;
        }}

        QComboBox {{
            background-color: #FFFFFF;
            color: #1A1A2E;
            border: 1px solid #D0D5DD;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
        }}
        QComboBox:focus {{ border-color: #1F6FEB; }}
        QComboBox:disabled {{ color: #999; background-color: #F0F2F5; }}
        QComboBox::drop-down {{ border: none; padding-right: {Spacing.SM}px; }}
        QComboBox QAbstractItemView {{
            background-color: #FFFFFF;
            color: #1A1A2E;
            border: 1px solid #D0D5DD;
            selection-background-color: #1F6FEB;
            selection-color: #FFFFFF;
            outline: none;
        }}

        QCheckBox {{
            color: #555;
            spacing: {Spacing.SM}px;
            background-color: transparent;
        }}
        QCheckBox::indicator {{
            width: 16px; height: 16px;
            border: 1px solid #D0D5DD;
            border-radius: {Radius.SM}px;
            background-color: #FFFFFF;
        }}
        QCheckBox::indicator:checked {{
            background-color: #1F6FEB; border-color: #1F6FEB;
        }}

        QSpinBox {{
            background-color: #FFFFFF; color: #1A1A2E;
            border: 1px solid #D0D5DD;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
        }}
        QSpinBox:focus {{ border-color: #1F6FEB; }}

        QProgressBar {{
            background-color: #E8EAED; color: #1A1A2E;
            border: 1px solid #D0D5DD;
            border-radius: {Radius.MD}px;
            text-align: center; min-height: 24px;
            font-weight: bold; font-size: 12px;
        }}
        QProgressBar::chunk {{
            background-color: #1F6FEB;
            border-radius: {Radius.MD - 1}px;
        }}

        QScrollBar:vertical {{
            background-color: transparent; width: 8px; margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background-color: #C0C4CC; border-radius: {Radius.PILL}px; min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{ background-color: #999; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar:horizontal {{
            background-color: transparent; height: 8px; margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background-color: #C0C4CC; border-radius: {Radius.PILL}px; min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{ background-color: #999; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

        QMessageBox {{ background-color: #FFFFFF; }}
        QMessageBox QLabel {{ color: #1A1A2E; }}

        QMenu {{
            background-color: #FFFFFF; color: #1A1A2E;
            border: 1px solid #D0D5DD;
            border-radius: {Radius.MD}px; padding: {Spacing.XS}px;
        }}
        QMenu::item {{
            padding: {Spacing.SM}px {Spacing.XL}px; border-radius: {Radius.SM}px;
        }}
        QMenu::item:selected {{ background-color: #1F6FEB; color: #FFFFFF; }}
    """)
