import curses
import gspread
from google_credentials import username, password
from textwrap import fill


class MainTerminal:
    """Class to manage the loading and refreshing of the main terminal."""

    def __init__(self,
                 main_term_h,
                 main_term_w,
                 main_term_y,
                 main_term_x,
                 main_menu_ss_title='terminal_menus',
                 main_menu_wks_title='basic_menu',):
        """Init function TODO this docstring."""
        print "trying to init the curses new window for MainTerminal."
        self.main_term = curses.newwin(main_term_h, main_term_w,
                                       main_term_y, main_term_x)
        print "made the new MainTerminal window"
        self.main_term_h = main_term_h
        self.main_term_w = main_term_w

        self.gc = gspread.login(username, password)
        self.main_menu_ss_title = main_menu_ss_title
        self.main_menu_wks_title = main_menu_wks_title
        
        self.current_ss_title = main_menu_ss_title
        self.current_ss = self.gc.open(self.current_ss_title)
        self.current_wks_title = self.main_menu_wks_title
        
        self.current_menu_dict = {}
        self.current_menu_str = ""
        
    def parse_menu(
            self,
            wks_title=None,
            ss_title=None,
            max_width=None,
    ):
        """Parses the given spreadsheet and output the menu in the form of a string and a dict"""

        pass

        if wks_title == None:
            wks_title = self.main_menu_wks_title
        else:
            self.current_wks_title = wks_title

        if ss_title == None:
            ss_title=self.main_menu_ss_title
        elif ss_title != self.current_ss_title:
            self.current_ss_title = ss_title
            self.current_ss = gc.open(spreadsheet_title)
        else:
            # If the program is here, it should be because the
            # ss_title was not defined, or its the same as the
            # current_ss
            pass

        if max_width == None:
            max_width = self.main_term_w-1
            
            
        tmp_menu_list = self.current_ss.worksheet(self.current_wks_title).get_all_values()

        tmp_menu_dict = {}
        tmp_menu_headers = tmp_menu_list.pop(0)
        tmp_menu_headers.pop(0)
        for i in tmp_menu_list:
            tmp_menu_dict[i[0]] = {}
            for j, k in enumerate(tmp_menu_headers, start=1):
                tmp_menu_dict[i[0]][k] = i[j]

        tmp_str = ""
        tmp_str = fill(
                    tmp_menu_dict['description']['description'],  width=max_width
                ) + "\n"
        tmp_menu_options = [x for x in tmp_menu_dict.keys() if x.find('option_')!=-1]
        # TODO get it to capture the number from the key
        tmp_menu_options.sort()
        for i, j in enumerate(tmp_menu_options, start=1):
            tmp_str += str(i)  + ") " + tmp_menu_dict[j]['description'] + "\n"

        # Assign the new variables
        self.current_menu_dict = tmp_menu_dict
        self.current_menu_str = tmp_str

    def redraw(self):
        """Erases and noutrefreshes terminal."""
        self.main_term.erase()
        self.main_term.addstr(0, 0, self.current_menu_str)
        self.main_term.noutrefresh()

    def current_options(self):
        """Returns current options available in form of a dictionary."""

        tmp_dict = {}
        for i in self.current_menu_dict.keys():
            # TODO make this extract the number from the string
            if i.find("option_") != 1:
                tmp_dict[i] = self.current_menu_dict[i]

        return tmp_dict

        
