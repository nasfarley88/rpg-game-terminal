import curses

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
