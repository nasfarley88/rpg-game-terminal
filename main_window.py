import curses
import multiprocessing
from google_credentials import username, password
import gspread
from textwrap import fill
from pyfiglet import figlet_format

class MenuProcessor(multiprocessing.Process):
    """This class deals with caching menus and fetching new menus from
    Google Docs.

    """
    def __init__(self, max_width):
        "Initialise the thread for updating the window"
        multiprocessing.Process.__init__(self)

        self.kill_event = multiprocessing.Event()

        self.gc = gspread.login(username, password)

        # ip == input pipe and op == output pipe
        self.menu_str_op, self.menu_str_ip = multiprocessing.Pipe()
        self.menu_dict_op, self.menu_dict_ip = multiprocessing.Pipe()

        self.ss_title_op, self.ss_title_ip = multiprocessing.Pipe()
        self.wks_title_op, self.wks_title_ip = multiprocessing.Pipe()

        self.max_width = max_width

    def shutdown(self):
        """Stop the process for managing the chache and menu fetching. """
        self.kill_event.set()


    def fetch_data(self, ss_title, wks_title):
        """Signal to the run loop that data should be fetched """
        self.ss_title_ip.send(ss_title)
        self.wks_title_ip.send(wks_title)

    # TODO: properly check that max_width doesn't go crazy
    def parse_data(self, wks_as_list, max_width=40):
        """Parse the data fetched by the run loop. 

        Recieves chosen worksheet as a list and interprets it in
        the form of a dictionary and a string.

        returns (dict, str)

        """

        menu_dict = {}
        menu_str = "list processing"

        menu_headers = wks_as_list.pop(0)
        menu_headers.pop(0)
        for i in wks_as_list:
            menu_dict[i[0]] = {}
            for j, k in enumerate(menu_headers, start=1):
                menu_dict[i[0]][k] = i[j]

        try:
            menu_str = figlet_format(
                "* " + menu_dict['title']['description'],
                font='smslant'
                )
        except:
            menu_str = fill(str(menu_dict))
                
        menu_str += fill(
                    menu_dict['description']['description'],  width=max_width
                ) + "\n"
        menu_options = [x for x in menu_dict.keys() if x.find('option_')!=-1]
        # TODO get it to capture the number from the key
        menu_options.sort()
        for i, j in enumerate(menu_options, start=1):
            menu_str += str(i)  + ") " + menu_dict[j]['description'] + "\n"

        # return (menu_dict, menu_str)
        return(menu_dict, menu_str)

    def run(self):
        """The running loop for this process. """
        while not self.kill_event.is_set():
            if self.ss_title_op.poll() and self.wks_title_op.poll():

                ss_title = self.ss_title_op.recv()
                wks_title = self.wks_title_op.recv()

                # TODO: Make it so that it caches stuff
                curr_ss = self.gc.open(ss_title)
                curr_wks = curr_ss.worksheet(wks_title).get_all_values()

                tmp_dict, tmp_str = self.parse_data(curr_wks, self.max_width)

                self.menu_dict_ip.send(tmp_dict)
                self.menu_str_ip.send(tmp_str)

        print "Exited run loop."

class MainWindow():
    """This is a class to control the main window. """

    def center_text(self, str_to_format):
        """A simple function to center text. Returns string. """

        dimen_y, dimen_x = self.window.getmaxyx()
        str_dimen_y = len(str_to_format.splitlines())
        # A little bit of python 'magic' from
        # http://stackoverflow.com/questions/873327/pythons-most-efficient-way-to-choose-longest-string-in-list
        str_dimen_x = len(max(str_to_format.splitlines(), key=len))
        tmp_list = []
        for i in str_to_format.splitlines():
            tmp_list.append(' '*((dimen_x-str_dimen_x)/2) + i)
        str_to_format = "\n".join(tmp_list)
        str_to_format = ((dimen_y-str_dimen_y)/2)*"\n" + str_to_format

        return str_to_format


    def center_text_horiz_block(self, str_to_format):
        """A simple function to center text horizontally. Returns string. """

        dimen_y, dimen_x = self.window.getmaxyx()
        str_dimen_y = len(str_to_format.splitlines())
        # A little bit of python 'magic' from
        # http://stackoverflow.com/questions/873327/pythons-most-efficient-way-to-choose-longest-string-in-list
        str_dimen_x = len(max(str_to_format.splitlines(), key=len))
        tmp_list = []
        for i in str_to_format.splitlines():
            tmp_list.append(' '*((dimen_x-str_dimen_x)/2) + i)
        str_to_format = "\n".join(tmp_list)

        return str_to_format

    def __init__(
            self,
            nlines,
            ncols,
            begin_y,
            begin_x,
            ss_title='terminal_menus',
            wks_title='basic_menu'):
        """Initialise the curses window and start an MenuProcessor. """
        self.window = curses.newwin(nlines, ncols, begin_y, begin_x)

        self.ss_title = ss_title
        self.wks_title = wks_title

        self.curr_menu_dict = {}
        self.curr_menu_str = self.center_text(figlet_format("ODIN 2.01", font='slant'))

        # TODO: Make sure the window prints something before
        # menu_processor begins. This will ensure that the user does
        # not panic as it starts up

        self.menu_processor = MenuProcessor(max_width=ncols-1)
        self.menu_processor.start()

    def fetch_menu(self, ss_title=None, wks_title=None):

        if ss_title == None:
            ss_title = self.ss_title
        else:
            self.ss_title = ss_title

        if wks_title == None:
            wks_title = self.wks_title
        else:
            self.wks_title = wks_title
            
        self.curr_menu_dict = {}
        self.curr_menu_str = self.center_text(figlet_format("loading", font='smslant'))
        self.menu_processor.fetch_data(ss_title, wks_title)

    def redraw(self):
        """Redraw this window. """

        if self.menu_processor.menu_dict_op.poll() and self.menu_processor.menu_str_op.poll():
            self.curr_menu_dict = self.menu_processor.menu_dict_op.recv()
            self.curr_menu_str = self.menu_processor.menu_str_op.recv()
        self.window.erase()
        self.window.addstr(0, 0, self.curr_menu_str)
        self.window.noutrefresh()

            
            
    
    
