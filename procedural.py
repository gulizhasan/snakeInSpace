import random
import curses


def create_food(snake, window):
    food = None
    while food is None:
        food = [random.randint(1, curses.COLS - 2),
                random.randint(1, curses.LINES - 2)]
        if food in snake:
            food = None
    window.addch(food[1], food[0], curses.ACS_PI)
    return food


def snake_game(stdscr):
    curses.curs_set(0)
    stdscr.timeout(100)

    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)

    snake = [[4, 4], [4, 3], [4, 2]]
    food = create_food(snake, w)

    key = curses.KEY_RIGHT

    while True:
        next_key = w.getch()
        key = key if next_key == -1 else next_key

        new_head = [snake[0][0], snake[0][1]]

        if key == curses.KEY_DOWN:
            new_head[1] += 1
        elif key == curses.KEY_UP:
            new_head[1] -= 1
        elif key == curses.KEY_LEFT:
            new_head[0] -= 1
        elif key == curses.KEY_RIGHT:
            new_head[0] += 1

        snake.insert(0, new_head)

        if (
            new_head[0] in [0, sw] or
            new_head[1] in [0, sh] or
            new_head in snake[1:]
        ):
            break

        if new_head == food:
            food = create_food(snake, w)
        else:
            tail = snake.pop()
            w.addch(tail[1], tail[0], ' ')

        w.addch(snake[0][1], snake[0][0], curses.ACS_CKBOARD)

    w.addstr(sh // 2, sw // 2, "Game Over", curses.A_BOLD)
    w.refresh()
    w.getch()


curses.wrapper(snake_game)
