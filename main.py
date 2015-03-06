#!/usr/bin/env python2

import curses
from time import sleep
from random import randint
from string import ascii_letters

from multiprocessing import Manager

manager = Manager()
# Joe holds all the variables for the threads
joe = manager.Namespace()

def create_hline_window(y_start, x_start, length):
    """Create a window with a single hline and return prepared window."""
    line = curses.newwin(
        1,
        length+1,
        y_start,
        x_start,
    )

    line.hline(0,0,"#", length)
    line.noutrefresh()

    return line


def create_vline_window(y_start, x_start, height):
    """Create a window with a single vline and return prepared window."""
    line = curses.newwin(
        height+1,
        1,
        y_start,
        x_start,
    )

    line.vline(0,0,"#", height)
    line.noutrefresh()

    return line


stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
stdscr.nodelay(1)
curses.curs_set(0)

begin_vec = {
    'x' : 0,
    'y' : 0,
}
size_vec = {
    'x' : 50,
    'y' : 80,
}

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


clock = curses.newwin(
    clock_h,
    clock_w,
    clock_y,
    clock_x,
)


news_ticker = curses.newwin(
    news_ticker_h,
    news_ticker_w,
    news_ticker_y,
    news_ticker_x,
)

from multiprocessing import Process

max_ticker_length = window_size_x-3

loading_news = " "*news_ticker_w
for i in range(5):
    loading_news += "Loading latest news..." + " "*news_ticker_w
joe.current_news = loading_news

def gui_that_ticks(_news_ticker, _clock, _joe):
    """Gui refreshing."""

    iter = 1
    # global current_news
    news = _joe.current_news
    previous_news = _joe.current_news
    
    lside_border = create_vline_window(0, 0, window_size_y)
    top_border = create_hline_window(0, 0, window_size_x)
    middle_border = create_hline_window(2, 0, window_size_x)
    bottom_border = create_hline_window(window_size_y-1, 0, window_size_x)
    rside_border = create_vline_window(0, window_size_x-1, window_size_y)
    curses.doupdate()
    
    # Add # before the clock.
    _clock.addch("#")

    while True:
        c = stdscr.getch()
        if c == ord('q'):
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()
            break

        lside_border.vline(0, 0, "#", window_size_y)
        lside_border.noutrefresh()

        for border in [top_border, middle_border, bottom_border]:
            border.hline(0,0,"#",window_size_x)
            border.noutrefresh()

        rside_border.vline(0, 0, "#", window_size_y)
        rside_border.noutrefresh()

        if iter % 10 == 0:
            time_hour = str(randint(10,99))
            time_minute = str(randint(10,99))
            _clock.addstr(0, 2, time_hour + ":" + time_minute)
            _clock.noutrefresh()
            
            pass
            
        if iter % 1 == 0:
            news = news[1:] + news[0]
            _news_ticker.addstr(0,1,news[:news_ticker_w-2])
            _news_ticker.noutrefresh()

        if iter % 100 == 0:
            latest_news = _joe.current_news.strip() + " "
            if latest_news != previous_news:
                news = latest_news
                previous_news = latest_news

        if iter == 999:
            iter = 0

        curses.doupdate()

        iter += 1
        # sleep(0.1)
        curses.napms(100)


print "Loading ODIN software..."
# The main menu
print "Connecting to ODIN..."
import gspread
print "Connected."

from google_credentials import username, password
gc = gspread.login(username, password)

terminal_menus = gc.open('terminal_menus')
current_menu = terminal_menus.worksheet('basic_menu').get_all_values()

current_news_sheet = gc.open('rpg_news')

gui_process = Process(target=gui_that_ticks, args=(news_ticker, clock, joe,))
gui_process.start()

while True:
    current_news_list = current_news_sheet.worksheet('current_news').get_all_values()
    tmp_list = []
    for i in range(4):
        # Take the first 3 news items and title from the first column
        try:
            tmp_list.append(current_news_list[i][0])
        except IndexError:
            pass
    joe.current_news = " ".join(tmp_list)

    sleep(10)

gui_process.join()

gui_process.terminate()

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
