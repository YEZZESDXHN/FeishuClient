from PySide6.QtWidgets import QMainWindow

from app.ui.MainWindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    自定义的主窗口类，继承了 QMainWindow（Qt主窗口行为）
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
