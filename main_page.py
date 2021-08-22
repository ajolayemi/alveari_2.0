#!/usr/bin/env python

""" Program's main GUI window. """
import sys

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

        self._add_wids()

        self._create_btn_connections()

    def _communicate_success(self):
        """ Communicates successful operation to user. """
        helper_functions.output_communicator(
            msg_box_font=MSG_FONT,
            window_title=WINDOW_TITLE,
            output_type=True,
            button_pressed=self.generate_order_btn.text()
        )

    def _communicate_failure(self):
        """ Communicates failed operation to user  """
        helper_functions.output_communicator(
            msg_box_font=MSG_FONT,
            window_title=WINDOW_TITLE,
            output_type=False,
            button_pressed=self.generate_order_btn.text()
        )

    def _create_btn_connections(self):
        """ Connects buttons signals to their corresponding slots. """
        self.close_btn.clicked.connect(self._close_btn_responder)

    def _close_btn_responder(self):
        """ Responds to user's click on the button named
        'Chiudi'. """
        user_choice = helper_functions.ask_before_close(
            msg_box_font=MSG_FONT,
            window_tile=WINDOW_TITLE
        )
        if user_choice == QMessageBox.Yes:
            self.close()

    def _add_wids(self):
        """ Adds necessary widgets. """
        user_name = helper_functions.get_user_name()
        self.greeting_lbl = QLabel(f'<h1> Ciao {user_name} </h1>')
        self.window_layout.addWidget(self.greeting_lbl)

        # Buttons
        self.generate_order_btn = QPushButton('Generare Spese')
        self.generate_order_btn.setFont(BUTTONS_FONT)
        self.generate_order_btn.setStyleSheet('color: blue')

        self.close_btn = QPushButton('Chiudi')
        self.close_btn.setFont(BUTTONS_FONT)
        self.close_btn.setStyleSheet('color: red')

        buttons_lst = [self.generate_order_btn, self.close_btn]

        self.form_layout_ = QFormLayout()

        for button_index, button_name in enumerate(buttons_lst):
            self.form_layout_.addRow(f'{button_index + 1}', button_name)

        self.window_layout.addLayout(self.form_layout_)


def main():
    app = QApplication(sys.argv)
    window = AlvMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
