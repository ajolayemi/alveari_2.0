#!usr/bin/env python

""" Handles communication between Python and Google Sheets API. """

from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.errors

from PyQt5.QtCore import QObject, pyqtSignal

# helper_modules is a self defined module
from helper_modules import helper_functions


ALV_API_KEY_JSON_FILE = 'alveari_api_key.json'
JSON_FILE_CONTENTS = helper_functions.json_file_loader(
    file_name=ALV_API_KEY_JSON_FILE)


class AlvApiThread(QObject):

    # Custom signals
    finished = pyqtSignal()
    unfinished = pyqtSignal()

    def __init__(self):
        super(AlvApiThread, self).__init__()
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.service_account_key_file = JSON_FILE_CONTENTS.get('api_key_file_name')
        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_key_file, scopes=self.scopes
        )
        self.spreadsheet_id = JSON_FILE_CONTENTS.get('spreadsheet_id')
        self.cell_range_to_read = JSON_FILE_CONTENTS.get('wb_cell_for_reading_range')
        self.cell_range_for_writing = JSON_FILE_CONTENTS.get('wb_cell_for_writing_range')
        self.cell_range_to_clear = JSON_FILE_CONTENTS.get('wb_cell_to_be_cleared_range')
