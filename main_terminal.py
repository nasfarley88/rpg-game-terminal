import curses
import gspread
from google_credentials import username, password
from textwrap import fill
from multiprocessing import Pipe, Process, Event

class MainTerminal:
    """Class to manage the loading and refreshing of the main terminal."""

    def _parse_menu(
            self,
            tmp_menu_list,
            max_width,
    ):
        """Parses the given spreadsheet and output the menu in the form of a dict and a str"""

        
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

        return (tmp_menu_dict, tmp_str)

    
    def menu_ss(
            self,
            ss_title_output_pipe,
            wks_title_output_pipe,
            curr_menu_dict_input_pipe,
            curr_menu_str_input_pipe,
            menu_ss_event,
            menu_ss_kill_event,
            max_width=79,
    ):

        gc = gspread.login(username, password)
        curr_ss_title = ""
        curr_wks_title = ""

        while True:
            if (menu_ss_event.is_set() and
                ss_title_output_pipe.poll() and
                wks_title_output_pipe.poll()):

                ss_title = ss_title_output_pipe.recv()
                wks_title = wks_title_output_pipe.recv()


                # If the spreadsheet title is different, load it up again
                if ss_title != curr_ss_title:
                    curr_ss = gc.open(ss_title)

                if wks_title != curr_wks_title:
                    curr_wks = curr_ss.worksheet(wks_title).get_all_values()

                tmp_dict, tmp_str = self._parse_menu(curr_wks, max_width)

                curr_menu_dict_input_pipe.send(tmp_dict)
                curr_menu_str_input_pipe.send(tmp_str)

                curr_ss_title = ss_title
                curr_wks_title = wks_title

                menu_ss_event.clear()

        ss_title_output_pipe.close()
        wks_title_output_pipe.close()
        curr_menu_dict_input_pipe.close()
        curr_menu_str_input_pipe.close()
            
        
    def __init__(self,
                 main_term_h,
                 main_term_w,
                 main_term_y,
                 main_term_x,
                 main_menu_ss_title='terminal_menus',
                 main_menu_wks_title='basic_menu',
    ):
        """Init function TODO this docstring."""
        print "trying to init the curses new window for MainTerminal."
        self.main_term = curses.newwin(main_term_h, main_term_w,
                                       main_term_y, main_term_x)
        print "made the new MainTerminal window"
        self.main_term_h = main_term_h
        self.main_term_w = main_term_w

        self.main_menu_ss_title = main_menu_ss_title
        self.main_menu_wks_title = main_menu_wks_title
        
        self.curr_ss_title = main_menu_ss_title
        # self.curr_ss = self.gc.open(self.curr_ss_title)
        self.curr_wks_title = self.main_menu_wks_title
        
        self.curr_menu_dict = {}
        self.curr_menu_str = ""

        self.ss_title_output_pipe, self.ss_title_input_pipe = Pipe()
        self.wks_title_output_pipe, self.wks_title_input_pipe = Pipe()

        self.curr_menu_dict_output_pipe, self.curr_menu_dict_input_pipe = Pipe()
        self.curr_menu_str_output_pipe, self.curr_menu_str_input_pipe = Pipe()

        self.menu_ss_event = Event()
        self.menu_ss_kill_event = Event()
        self.menu_ss_kill_event.clear()

        
        # Now, I create a thread to manage all the loading of spreadsheets
        self.menu_ss_process = Process(
            target=self.menu_ss,
            args=(
                self.ss_title_output_pipe,
                self.wks_title_output_pipe,
                self.curr_menu_dict_input_pipe,
                self.curr_menu_str_input_pipe,
                self.menu_ss_event,
                self.menu_ss_kill_event,
                self.main_term_w-1,
            )
        )
        self.menu_ss_process.start()

        
    def parse_menu(
            self,
            wks_title=None,
            ss_title=None,
            max_width=None,
    ):
        """A wrapper for parsing the menu so I can farm it out to a process. """

        # Wipe the menu so it won't accept commands anymore
        self.curr_menu_dict = {}

        max_y, max_x = self.main_term.getmaxyx()
        self.curr_menu_str = "\n"*(max_y/2) + " "*((max_x)/2-7) + "Loading menu..."
        # self.curr_menu_str = str(self.main_term.getmaxyx())

        if wks_title == None:
            wks_title = self.main_menu_wks_title
        else:
            self.curr_wks_title = wks_title

        if ss_title == None:
            ss_title=self.main_menu_ss_title
        elif ss_title != self.curr_ss_title:
            self.curr_ss_title = ss_title
        else:
            # You should never get here
            pass

        self.ss_title_input_pipe.send(ss_title)
        self.wks_title_input_pipe.send(wks_title)

        # When the pipes are full, tell the thread it's safe to proceed
        self.menu_ss_event.set()



    def redraw(self):
        """Erases and noutrefreshes terminal."""
        if self.curr_menu_str_output_pipe.poll():        
            self.curr_menu_str = self.curr_menu_str_output_pipe.recv()
        if self.curr_menu_dict_output_pipe.poll():
            self.curr_menu_dict = self.curr_menu_dict_output_pipe.recv()

        self.main_term.erase()
        self.main_term.addstr(0, 0, self.curr_menu_str)
        self.main_term.noutrefresh()

    def kill_menu_ss_process():
        """Simple. Does what it says."""
        # signal it's time to kill the thread
        menu_ss_kill_event.set()
        import time
        time.sleep(10)
        menu_ss_process.terminate()
        menu_ss_process.join()
