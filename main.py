#!/usr/bin/env python2

import curses
from linewindows import create_hline_window, create_vline_window
from main_terminal import MainTerminal
from time import sleep
from random import randint

from multiprocessing import Manager, Process

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






def gui_that_ticks(_joe):
    """Gui refreshing."""

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
    news_ticker = curses.newwin(news_ticker_h, news_ticker_w, news_ticker_y, news_ticker_x,)
    # main_term = curses.newwin(main_term_h, main_term_w, main_term_y, main_term_x,)
    main_term = MainTerminal(main_term_h, main_term_w, main_term_y, main_term_x,)
    

    loading_news = " "*news_ticker_w
    for i in range(5):
        loading_news += "Loading latest news..." + " "*news_ticker_w
    _joe.current_news = loading_news



    # terminal_menus = gc.open('terminal_menus')
    # current_menu_list = terminal_menus.worksheet('basic_menu').get_all_values()

    # current_news_sheet = gc.open('rpg_news')

    # current_menu_dict = {}
    # current_menu_headers = current_menu_list.pop(0)
    # current_menu_headers.pop(0)
    # for i in current_menu_list:
    #     current_menu_dict[i[0]] = {}
    #     for j, k in enumerate(current_menu_headers, start=1):
    #         current_menu_dict[i[0]][k] = i[j]
                
    iter = 0
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
            pass
        for i in range(1,10):
            if c == ord(str(i)):
                try:
                    # main_term.erase()
                    # main_term_string, visible_menu_dict = parse_menu(
                    #     wks_title=visible_menu_dict['option_'+str(i)]['action']
                    # )
                    main_term.parse_menu(
                        wks_title=main_term.current_menu_dict['option_' + str(i)]['action']
                    )
                except KeyError:
                    print "KeyError"
                    curses.napms(1000)
                    pass
            
        # main_term.addstr(0, 0, main_term_string)
        # main_term.noutrefresh()
        main_term.redraw()

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
            clock.addstr(0, 2, time_hour + ":" + time_minute)
            clock.noutrefresh()
            
            pass
            
        if iter % 1 == 0:
            news = news[1:] + news[0]
            news_ticker.addstr(0,1,news[:news_ticker_w-2])
            news_ticker.noutrefresh()

        if iter % 100 == 0:
            latest_news = _joe.current_news.strip() + " "
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

# def main_terminal_that_ticks(_joe):
#     """Code for the main screen.

#     This should (eventually) only be responsible for filling the
#     screen and doing animations. Network access should be farmed to a
#     separate thread to allow for 'Loading...' etc. to be displayed on
#     the screen (and avoid hanging).

#     """



#     while True:
#         main_terminal.addstr(2, 2, str(randint(1,1999)))
#         main_terminal.noutrefresh()
#         curses.napms(100)

# main_terminal_process = Process(target=main_terminal_that_ticks, args=(joe,))
# main_terminal_process.start()


# while True:
#     current_news_list = current_news_sheet.worksheet('current_news').get_all_values()
#     tmp_list = []
#     for i in range(4):
#         # Take the first 3 news items and title from the first column
#         try:
#             tmp_list.append(current_news_list[i][0])
#         except IndexError:
#             pass
#     joe.current_news = " ".join(tmp_list)

#     sleep(10)

gui_process.join()



curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
