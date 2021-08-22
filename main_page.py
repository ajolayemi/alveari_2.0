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
