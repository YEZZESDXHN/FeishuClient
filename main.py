import sys

from PySide6.QtWidgets import QApplication
from app.windows.MainWindow import MainWindow


if __name__ == "__main__":
    # main()
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    # app.setStyle("Fusion")
    w = MainWindow()
    # version = 'v0.1.9'
    # w.custom_status_bar.label_Version.setText(version)
    w.show()
    sys.exit(app.exec())