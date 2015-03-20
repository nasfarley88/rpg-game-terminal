import curses
import gspread
from google_credentials
from textwrap import fill
from multiprocessing import Pipe, Process

class MenuSpreadsheet:
    def __init__(self,
                 username=None,
                 password=None,
                 ss_title_output_pipe,
                 wks_title_output_pipe,
                 current_menu_dict_input_pipe,
                 current_menu_str_input_pipe,
    ):
        "Basically, a class that manages the spreadsheet loading etc."

        if username == None:
            self.username = google_credentials.username
        else:
            self.username = username

        if password == None:
            self.password = google_credentials.password
        else:
            self.password = password

        self.gc = gspread.login(username, password)

        del(self.password)
        del(self.username)

        
