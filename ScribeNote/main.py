import sys
from PyQt5.QtWidgets import QApplication
from app.ui import MainWindow
import os

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
