import ui.impl as setUi
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = setUi.ControlBoard()
    ui.startUi(window)
    window.show()
    sys.exit(app.exec_())
