#!/usr/bin/env python2
"""A simple terminal using Google spreadsheets as the menu. Meant for
casual RPG use.

"""

import curses
from linewindows import create_hline_window, create_vline_window
from main_terminal import MainTerminal
from time import sleep
from random import randint
from google_credentials import username, password

from multiprocessing import Manager, Process, Pipe

manager = Manager()
# Joe holds all the variables for the threads
joe = manager.Namespace()


stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
stdscr.nodelay(1)
curses.curs_set(0)

# max_ticker_length = window_size_x-3
import gspread
from google_credentials import username, password
gc = gspread.login(username, password)

def get_news(news_ticker_input_pipe, gc, max_news_items=3):
    """A simple function to obtain the news string and update it. """

    current_news_list = gc.open('rpg_news').worksheet('current_news').get_all_values()
    tmp_list = []
    for i in range(max_news_items+1):
        # Take the first 3 news items and the title from the first column
        try:
            tmp_list.append(current_news_list[i][0])
        except IndexError:
            pass

    news_ticker_input_pipe.send_bytes(" ".join(tmp_list) + " ")

def get_menu(menu_input_pipe, gc):
    """A simple function to fetch a menu. """
    pass
    
              
        

def gui_that_ticks(_joe):
    """Gui refreshing."""

    news_ticker_output_pipe, news_ticker_input_pipe = Pipe()
    menu_output_pipe, menu_input_pipe = Pipe()
    get_news_process = None
    # TODO: set up so that only one google connection is necessary
    gc = gspread.login(username, password)
    
    # Setting up window dimesions
    window_size_x = 80
    window_size_y = 24

    clock_w = 8
    clock_h = 1
    news_ticker_w = window_size_x - 2 - clock_w
    news_ticker_h = 1

    clock_y = 1
    clock_x = news_ticker_w + 1
    news_ticker_y = 1
    news_ticker_x = 1

    main_term_x = 2
    main_term_y = 3
    main_term_w = window_size_x - 2*main_term_x + 1
    main_term_h = window_size_y - main_term_y - 1

    clock = curses.newwin(clock_h, clock_w, clock_y, clock_x,)
    news_ticker = curses.newwin(news_ticker_h, news_ticker_w,
                                news_ticker_y, news_ticker_x,)
    main_term = MainTerminal(main_term_h, main_term_w, main_term_y,
                             main_term_x,)
    

    loading_news = " "*news_ticker_w
    for i in range(5):
        loading_news += "Loading latest news..." + " "*news_ticker_w
    _joe.current_news = loading_news


    iter = 0
    # global current_news
    news = _joe.current_news
    previous_news = _joe.current_news
    latest_news = _joe.current_news
    
    lside_border = create_vline_window(0, 0, window_size_y)
    top_border = create_hline_window(0, 0, window_size_x)
    middle_border = create_hline_window(2, 0, window_size_x)
    bottom_border = create_hline_window(window_size_y-1, 0, window_size_x)
    rside_border = create_vline_window(0, window_size_x-1, window_size_y)
    curses.doupdate()
    
    # Add # before the clock.
    clock.addch("#")

    # This string should be huge. But never wider than 76 characters
    # main_term_string = ""
    # main_term.addstr(0, 0, main_term_string)
    visible_menu_dict = {}
    while True:
        c = stdscr.getch()
        if c == ord('q'):
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()
            break
        elif c == ord('h'):
            main_term.parse_menu()

        for i in range(1,10):
            if c == ord(str(i)):
                try:
                    main_term.parse_menu(
                        wks_title=main_term.current_menu_dict['option_' + str(i)]['action']
                    )
                except KeyError:
                    pass
            
        main_term.redraw()

        lside_border.vline(0, 0, "#", window_size_y)
        lside_border.noutrefresh()

        for border in [top_border, middle_border, bottom_border]:
            border.hline(0,0,"#",window_size_x)
            border.noutrefresh()

        rside_border.vline(0, 0, "#", window_size_y)
        rside_border.noutrefresh()


        # TODO change this to 10 or whatever
        if iter % 1 == 0:
            # time_hour = str(randint(10,99))
            # time_minute = str(randint(10,99))
            # clock.addstr(0, 2, time_hour + ":" + time_minute)
            clock.addstr(0, 2, str(news_ticker_output_pipe.poll()))
            clock.noutrefresh()
            
        if iter % 1 == 0:
            # News ticker action
            news = news[1:] + news[0]
            news_ticker.addstr(0,1,news[:news_ticker_w-2])
            news_ticker.noutrefresh()

        if iter % 100 == 0:
            if get_news_process == None or not get_news_process.is_alive():
                get_news_process = Process(
                    target=get_news,
                    args=(
                        news_ticker_input_pipe,
                        gc,
                    )
                )
                get_news_process.start()

        # This should always happen after at least one get_news_process
        # has started
        if iter % 10 == 0:
            if (not get_news_process.is_alive()
                and news_ticker_output_pipe.poll()):
                latest_news = news_ticker_output_pipe.recv_bytes()
                # latest_news = " ".join(latest_news)
            if latest_news != previous_news:
                news = latest_news
                previous_news = latest_news


        # 10 000 iterations means about 15 minutes
        if iter == 9999:
            iter = 0

        curses.doupdate()

        iter += 1
        # sleep(0.1)
        curses.napms(100)


print "Loading ODIN software..."
# The main menu
print "Connecting to ODIN..."

print "Connected."

gui_process = Process(target=gui_that_ticks, args=(joe,))
gui_process.start()
gui_process.join()

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
