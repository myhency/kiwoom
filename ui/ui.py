from app.main import *
from PyQt5.QtWidgets import *
import sys


class UIClass():
    def __init__(self):
        print("UIClass 입니다")

        self.app = QApplication(sys.argv)

        self.main = Main()

        self.app.exec_()
