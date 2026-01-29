"""HardSubForge - Aplicativo de conversão de vídeo para streaming."""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    """Função principal da aplicação."""
    app = QApplication(sys.argv)
    app.setApplicationName("HardSubForge")
    app.setOrganizationName("HardSubForge")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
