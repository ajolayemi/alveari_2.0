#!/usr/bin/env python

""" Handles communication between Python and Google Sheets API. """

from PyQt5.QtCore import QObject, pyqtSignal
from google.oauth2 import service_account
from googleapiclient.discovery import build
from math import floor
import pandas as pd
# helper_modules is a self defined module
from helper_modules import helper_functions

ALV_API_KEY_JSON_FILE = 'alveari_api_key.json'
GOOGLE_SHEETS_INFO_JSON = 'google_sheet_info.json'
JSON_FILE_CONTENTS = helper_functions.json_file_loader(
    file_name=GOOGLE_SHEETS_INFO_JSON)
BOX_CAPACITY = 100


class AlvApiThread(QObject):

    # Custom signals
    started = pyqtSignal()
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

    def manual_generator(self):
        # The following statements clears existing data in the workbook
        self.api_service.spreadsheets().values().batchClear(
            spreadsheetId=self.spreadsheet_id,
            body={'ranges': self.cell_range_to_clear}
        ).execute()

        # A list to store the orders that have been processed
        processed_orders = []
        # Get all order nums
        order_numbers = self.get_all_order_numbers()

        final_data = []
        self.started.emit()
        for current_order_num in order_numbers:
            if current_order_num in processed_orders:
                continue
            else:
                client_total_boxes = self.get_tot_box(
                    order_num=current_order_num)
                box_dict = helper_functions.build_box_dict(
                    total_box=int(client_total_boxes)
                )
                client_order = self.get_client_order(
                    order_num=current_order_num
                )
                if client_order:
                    for current_order in client_order:
                        product_id = current_order[2]
                        product_name = current_order[3]
                        ordered_qta = int(current_order[5])
                        product_ratio = int(current_order[6])
                        order_code = self.get_order_code(
                            order_num=current_order_num,
                            product_id=product_id)

                        # Variable to keep track of the quantity od a product
                        # that has already been satisfied
                        qta_satisfied = 0

                        # Another variable called remainder to keep track of the
                        # remaining quantity to be satisfied
                        remainder = int(ordered_qta - qta_satisfied)

                        for box in box_dict:
                            # Get available space
                            available_space = BOX_CAPACITY - box_dict.get(box)

                            # If the remainder value is 0
                            if remainder == 0:
                                # Add the current order_number to processed order list
                                processed_orders.append(current_order_num)

                                # Break the loop that goes through box_dict
                                break

                            # If the current box is already full
                            if box_dict[box] >= BOX_CAPACITY:
                                continue

                            if ordered_qta != qta_satisfied:
                                # Get the required space, i.e the space needed in a
                                # box for the current product
                                required_space = helper_functions.get_occupation_percent(
                                    product_ratio, current_qta=remainder)
                                # If the required space is <= the current available space
                            if required_space <= available_space:
                                # add the following info into the list of data that will be
                                # written later in the google sheet workbook
                                data = [order_code, product_id, product_name,
                                        remainder, box, 'di', client_total_boxes]
                                final_data.append(data)
                                final_occupation = round(
                                    (remainder / product_ratio) * BOX_CAPACITY)

                                # Modify the necessary values
                                qta_satisfied += remainder
                                remainder = int(ordered_qta - qta_satisfied)
                                box_dict[box] += final_occupation

                            elif required_space > available_space:
                                currently_available_space = available_space / BOX_CAPACITY
                                # This means the possible qta of a product that can enter the
                                # currently available_space
                                possible_qta = round(currently_available_space * product_ratio)

                                if possible_qta <= 0:
                                    continue
                                else:
                                    qta_satisfied += possible_qta
                                    remainder = ordered_qta - qta_satisfied

                                    final_occupation = round((possible_qta / product_ratio) * BOX_CAPACITY)
                                    box_dict[box] = final_occupation
                                    data = [order_code, product_id, product_name, possible_qta,
                                            box, 'di', client_total_boxes]
                                    final_data.append(data)

                    # While exiting the loop that goes over client's order
                    # Check to see that all boxes have being completed
                    incomplete_boxes = list(filter(lambda x: box_dict[x] < 100, box_dict))
                    filler_det = self.get_order_filler_det(
                        order_num=current_order_num)
                    found_empty_box = False
                    if filler_det:
                        order_code = filler_det[0][0]
                        filler_id = filler_det[0][2]
                        filler_name = filler_det[0][3]
                        filler_qta = filler_det[0][5]
                    else:
                        pass

                    for box in incomplete_boxes:
                        if box == incomplete_boxes[-1] and not found_empty_box:
                            data = [order_code, filler_id, filler_name,
                                    filler_qta, box, 'di', client_total_boxes]
                            final_data.append(data)
                        elif box_dict[box] > 0:
                            pass
                        else:
                            found_empty_box = True
                            data = [order_code, filler_id, filler_name,
                                    filler_qta, box, 'di', client_total_boxes]
                            final_data.append(data)
        # At the end
        write_data_request = self.api_service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=self.cell_range_for_writing,
            valueInputOption='USER_ENTERED',
            insertDataOption='OVERWRITE',
            body={'values': final_data}
        )
        response = write_data_request.execute()
        print(response)

    def get_order_filler_det(self, order_num):
        return list(filter(lambda x: all((x[4] == 'Riempimento',
                                          x[1] == order_num)), self.all_wb_content))

    def get_order_code(self, order_num: str, product_id):
        """ Return the order_code associated with an order_num and a product with
        product_id. """
        order_content = list(filter(
            lambda x: all((x[1] == order_num, x[2] == product_id)),
            self.all_wb_content))
        return order_content[0][0] if order_content else ''

    def get_client_order(self, order_num: str) -> list[list]:
        """ Returns a nested list of what a client with the provided order_num
        has ordered. """
        return list(filter(lambda x: all((x[4] != "CUSTOM SET", x[4] != 'Riempimento',
                                          x[1] == order_num)), self.all_wb_content))

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

        all_values = wb_contents.get('values', [])[1:]
        return sorted(all_values, key=lambda x: x[4])

    def _create_api_service(self):
        self.api_service = build('sheets', 'v4', credentials=self.creds)
        self.sheet_api = self.api_service.spreadsheets()


if __name__ == '__main__':
    pass
