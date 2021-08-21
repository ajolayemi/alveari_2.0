#!/usr/bin/env python

""" Handles communication between Python and Google Sheets API. """

from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.errors

from PyQt5.QtCore import QObject, pyqtSignal

# helper_modules is a self defined module
from helper_modules import helper_functions


ALV_API_KEY_JSON_FILE = 'alveari_api_key.json'
GOOGLE_SHEETS_INFO_JSON = 'google_sheet_info.json'
JSON_FILE_CONTENTS = helper_functions.json_file_loader(
    file_name=GOOGLE_SHEETS_INFO_JSON)


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

        self.api_service = None
        self.sheet_api = None

        self._create_api_service()

        self.all_wb_content = self.get_all_wb_contents()

    def get_tot_box(self, order_num: str) -> int:
        """ Returns the quantity of cubotto (boxes) ordered by a client
        with the specified order_num. """
        order_content = list(filter(lambda x: x[4] == "CUSTOM SET" and x[1] == order_num, self.all_wb_content))
        return int(order_content[0][5]) if order_content else 0

    def get_all_order_numbers(self):
        """ Returns a list of all clients' order numbers. """
        order_nums = []
        for order_content in self.all_wb_content[1:]:
            if order_content[1] not in order_nums:
                order_nums.append(order_content[1])
        return order_nums

    def get_all_wb_contents(self):
        """ Uses the sheet api connection established with Google Sheet
        to retrieve all the data contained in the workbook where clients
        orders are stored. """
        wb_contents = self.sheet_api.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.cell_range_to_read).execute()

        return wb_contents.get('values', [])

    def _create_api_service(self):
        self.api_service = build('sheets', 'v4', credentials=self.creds)
        self.sheet_api = self.api_service.spreadsheets()


if __name__ == '__main__':
    print(AlvApiThread().get_tot_box(order_num='493 - 202'))