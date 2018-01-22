__author__ = 'kenneche'

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import sys
import datetime
import requests
import os
import numpy as np
import pandas as pd


class MyParser:

    def __init__(self):
        self.data_set = []
        self.num = []
        self.equipment_list = []
        self.search_num = ""

    def main_noarg(self):
        number = input("Please enter the CIS number: ")
        self.main(number)

    def main(self, text):
        # Prompt user for a CIS number
        if text is "":
           self.main_noarg()
        else:
            number = text

            if ',' in number:
                self.num = number.split(",")
                # self.num.sort(key=int)
            else:
                self.num.append(number)

            print("CIS number: {0}".format(self.num))

            # This will use the requests module to generate a request.
            login_url = "https://e3.selabs.com/facets/login"
            data = {'application':'Extranet', 'login':'kenneche', 'password':'ender0662'}
            s = requests.session()  # Create a Session
            s.post(login_url, data=data)  # Enter login information for the login screen

            # Jump directly to search CIS number page.
            s_url = "https://e3.selabs.com/facets/main?NextURL=/NewExtranet/Equipment/SearchByIdentifiers.jsp"
            s.get(s_url)  # use session to retrieve the content of the search page.

            # Enter CIS into request to POST
            search_form_url = "https://e3.selabs.com/facets/main"
            for n in self.num:
                sid_data = {'TransactionName':'com.selabs.e3.tx.extranet.SearchEquipmentByLineNumber',
                                 'NextURL':'/NewExtranet/Equipment/EquipmentDetails.jsp',
                                 'RequestPage':'IdentifierSearch',
                                 'TransactionParameter_0_Integer':n}
                sid_req = s.post(search_form_url, data=sid_data)
                sid_results = sid_req.text

                # Use BeautifulSoup4 to parse the results
                soup = BeautifulSoup(sid_results, 'html.parser')
                data_table = soup.find("table", "data")
                cal_table = soup.find("table", "details")
                data_cells = self.get_table_contents(data_table)
                cal_cells = self.get_table_contents(cal_table)

                # Get the cell contents
                cis = self.get_cis_number(data_cells)
                mfg = self.get_manufacturer(data_cells)
                model = self.get_model(data_cells)
                description = self.get_description(data_cells)
                cal_end_date = self.get_recall_date(data_cells)
                cal_cycle = self.get_cal_cycle(data_cells)
                cal_start_date = self.calc_cal_start_date(cal_end_date, cal_cycle)

                # Get Past Service Records.  This is located on a different URL.
                menu_table = soup.find("table", "menu")

                print("CIS = {0}, Manufacturer = {1}, "
                      "Model = {2}, Description = {3}, "
                      "Cal Date = {4}, Cal Due Date = {5}, "
                      "Cal Cycle = {6}"
                      .format(cis, mfg, model, description, cal_start_date, cal_end_date, cal_cycle))

                result_data = [cis, mfg, model, description, cal_start_date, cal_end_date]
                self.data_set.append(result_data) # For Dataframe


            results_head = self.get_excel_header()
            df = pd.DataFrame.from_records(self.data_set, columns=results_head)

            # Sort the Dataframe by CIS number
            df_sort = df.sort_values(axis=0, by="CIS")
            print(df_sort.to_string())

            # Write Dataframe to Excel
            df_sort.to_excel(self.generate_filename(), index=False)

    def get_content(self, text, arr):
        try:
            return arr[arr.index(text)+1]
        except ValueError:
            return "N/A"

    def get_cis_number(self, arr):
        cis_str = self.get_content("Line #", arr)
        try:
            return int(cis_str[4:])
        except:
            return int(cis_str)

    def get_manufacturer(self, arr):
        return self.normalize_text(self.get_content("Manufacturer", arr))

    def get_model(self, arr):
        return self.get_content("Model", arr)

    def get_description(self, arr):
        return self.normalize_text(self.get_content("Description", arr))

    def get_cal_end_date(self, arr):
        return self.normalize_date(self.get_content("Next Due", arr), "%d %b %Y")

    def get_recall_date(self, arr):
        return self.normalize_date(self.get_content("Recall Date", arr), "%d %b %Y")

    def get_cal_cycle(self, arr):
        return self.get_content("Cal Cycle", arr)

    def calc_cal_start_date(self, end_date, cycle):
        cycle_end_num = int(cycle[0:cycle.index(" ")])
        # Subtract the cycle number from the end date
        try:
            t = datetime.datetime.strptime(end_date, '%m/%d/%Y').date() + relativedelta(months=-cycle_end_num)
            new_date = datetime.datetime.combine(t, datetime.datetime.min.time()).strftime("%m/%d/%Y")
            return new_date
        except:
            return end_date  # return NA

    def get_table_contents(self, tbl):
        data_rows = tbl.find_all('tr')
        cell_data = []
        for row in data_rows:
            cells = row.find_all('td')
            for cell in cells:
                if cell.string is None:
                    cell_data.append("")
                else:
                    cell_data.append(cell.string)
        return cell_data

    def get_excel_header(self):
        return ["CIS",
                "Manufacturer",
                "Model",
                "Description",
                "Cal Date",
                "Cal Due Date"]

    # Auto-generate a filename based on the current date and time.
    #
    # Returns the directory and filename as a string.
    def generate_filename(self, extension='.xlsx'):
        current_date_time = datetime.datetime.now()
        strformat = current_date_time.strftime("%Y%m%d_%H%M%S")
        dir = os.path.dirname(os.path.abspath(__file__)) + os.sep + "Results" + os.sep
        str_path = dir + strformat + extension
        return str_path

    def load_excel(self, f):   # f is the filename path
        dir = os.path.dirname(os.path.abspath(__file__)) + os.sep + "Results"
        if os.path.exists(dir):
            os.chdir(dir)
        wb = openpyxl.load_workbook(f, read_only=True)
        sheet = wb.get_sheet_by_name('Sheet')
        num = self.read_from_excel(sheet, 1)
        self.main(num)


    # Returns all entries in a column
    def read_from_excel(self, sheet, col):
        num = ""
        row = 2
        try:
            while sheet.cell(row=row, column=col).value != "":
                entry = sheet.cell(row=row, column=col).value
                print("read_from_excel: (row={0}, col={1}) entry={2}".format(row,col,entry))
                num = num + entry + ","
                row += 1
        except:
            if num[-1] == ",": #strip the last comma
                num = num[:-1]
            print("read_from_excel: arr={0}".format(num))
        return num

    def normalize_date(self, string_date, input_date_format):
        try:
            if string_date.lower() == 'n/a':
                return "NA"
            else:
                dt = datetime.datetime.strptime(string_date, input_date_format)
                return dt.strftime("%m/%d/%Y")
        except ValueError as e:
            print("ValueError: ({0}): {1}".format(e.errno, e.strerror))

    """
    normalize_text takes a string and reduces all the characters to lower case.  Then it changes the first
    character of each word to upper case.
    """
    def normalize_text(self, text):
        t = []
        tmp = ""
        if len(text) > 0:
            if ' ' in text:  # more than one word
                t = text.split(" ")
                for word in t:
                    tmp = tmp + self.normalize_text_word(word) + " "
                tmp.rstrip()  # remove trailing whitespace
            else:  # one word
                tmp = self.normalize_text_word(text)
        else:  # no word
            tmp = text
        return tmp

    """
    normalize_text_word takes a word and changes all its characters to lower case.
    Then it capitalizes the first character.
    For those in the exempt list, this action is ignored and the original returned.
    """
    def normalize_text_word(self, word):
        if self.exempt_list(word) is False:
            if len(word) > 0:  # Checks for empty string
                word = word[0].upper() + word[1:].lower()
        return word

    """
    Opens the file named exempt_list.txt
    Compares the input to each element in the text file.
    If match, then return True.
    Otherwise, return False.
    """
    def exempt_list(self, text):
        with open("exempt_list.txt", "r") as exempt_file:
            for line in exempt_file:
                newline = line.splitlines()
                if text == newline[0]:
                    return True
            return False



    def test(self):
        # self.load_excel("20160414_151411.xlsx")
        num1 = 45050  # Hard-coded for debug purpose.  This number is for the Rohde & Schwarz ESCI EMI Receiver.
        num2 = 37017  # Hard-coded for debug purpose.  This number is for a Fluke 175 True RMS Multimeter.
        num_list = str(num1) + "," + str(num2)
        app.main(num_list)
        pass


if __name__ == '__main__':
    app = MyParser()
    # print(sys.argv)
    app.main_noarg()
    # app.test()
