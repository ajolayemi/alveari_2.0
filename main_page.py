#!/usr/bin/env python

""" Program's main GUI window. """

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QMainWindow, QWidget,
                             QVBoxLayout, QApplication,
                             QLabel, QPushButton, QFormLayout,
                             QMessageBox)

from helper_modules import helper_functions
from alv_api_communicator import AlvApiThread

MSG_FONT = QFont('Italics', 13)
BUTTONS_FONT = QFont('Times', 13)
SPREADSHEET_INFO_JSON_FILE = 'google_sheet_info.json'

JSON_FILE_CONTENT = helper_functions.json_file_loader(
    file_name=SPREADSHEET_INFO_JSON_FILE
)
WINDOW_TITLE = JSON_FILE_CONTENT.get('window_title')


class AlvMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(AlvMainWindow, self).__init__(parent)
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(300, 110)
        self.central_widget = QWidget()
        self.window_layout = QVBoxLayout()

        self.central_widget.setLayout(self.window_layout)
        self.setCentralWidget(self.central_widget)


