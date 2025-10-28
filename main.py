# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets

from ui_mainwindow import Ui_MainWindow
from widgets import TabSection
from slots import MainWindowSlots

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, MainWindowSlots):
    """Main window of the application."""
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.connect_slot()

    def connect_slot(self):
        """Connect signals and slots."""
        self.add_section_button.clicked.connect(lambda: self.add_section(TabSection))
        self.delete_section_button.clicked.connect(self.delete_section)
        self.build_button.clicked.connect(self.build)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()