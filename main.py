import sys
from PyQt5.QtWidgets import QApplication
from gui.app import MainWindow

import matplotlib
matplotlib.use('Qt5Agg')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()