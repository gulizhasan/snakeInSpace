import random
import curses
import time

def create_food(snake, window, sh, sw):
    food = None
    while food is None:
        food = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
        if food in snake:
            food = None
    window.addch(food[0], food[1], curses.ACS_PI)
    return food

def create_meteors(snake, food, window, sh, sw, num_meteors=5):
    meteors = []
    while len(meteors) < num_meteors:
        meteor = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
        if meteor not in snake and meteor != food:
            window.addch(meteor[0], meteor[1], '*', curses.color_pair(1))
            meteors.append(meteor)
    return meteors

def create_portals(snake, food, meteors, window, sh, sw):
    portals = []
    while len(portals) < 2:
        portal = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
        if portal not in snake and portal != food and portal not in meteors:
            portals.append(portal)
    return portals

def snake_game(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)

    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(100)

    score = 0

    snake_x = sw//4
    snake_y = sh//2
    snake = [[snake_y, snake_x], [snake_y, snake_x-1], [snake_y, snake_x-2]]

    food = create_food(snake, w, sh, sw)
    w.addch(food[0], food[1], curses.ACS_PI)

    meteors = create_meteors(snake, food, w, sh, sw)

    portals = create_portals(snake, food, meteors, w, sh, sw)
    for portal in portals:
        w.addch(portal[0], portal[1], 'O', curses.color_pair(2))

    key = curses.KEY_RIGHT

    # Draw borders using 'X' characters, adjusted to stay within window bounds
    for y in range(sh):
        w.addch(y, 0, 'X')
        w.addch(y, sw - 2, 'X')  # Change from sw - 1 to sw - 2
    for x in range(sw - 1):  # Change from sw to sw - 1
        w.addch(0, x, 'X')
        w.addch(sh - 1, x, 'X')

    while True:
        next_key = w.getch()
        key = key if next_key == -1 else next_key

        if key == curses.KEY_DOWN:
            new_head = [snake[0][0] + 1, snake[0][1]]
        elif key == curses.KEY_UP:
            new_head = [snake[0][0] - 1, snake[0][1]]
        elif key == curses.KEY_LEFT:
            new_head = [snake[0][0], snake[0][1] - 1]
        elif key == curses.KEY_RIGHT:
            new_head = [snake[0][0], snake[0][1] + 1]

        snake.insert(0, new_head)

        if snake[0] == food:
            score += 1
            food = create_food(snake, w, sh, sw)
            w.addch(food[0], food[1], curses.ACS_PI)
        else:
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        for portal in portals:
            if snake[0] == portal:
                exit_portal = portals[1] if portal == portals[0] else portals[0]
                snake.insert(0, [exit_portal[0], exit_portal[1]])
                break

        if snake[0][0] == 0 or snake[0][0] == sh-1 or snake[0][1] == 0 or snake[0][1] == sw-1:
            break
        if snake[0] in snake[1:]:
            break
        if snake[0] in meteors:
            break

        try:
            w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
        except:
            break

        # Display score
        score_str = f"Score: {score}"
        w.addstr(0, sw - len(score_str) - 2, score_str)

    w.clear()
    w.addstr(sh//2, sw//2 - len(f"Game Over! Score: {score}")//2, f"Game Over! Score: {score}")
    w.refresh()
    w.getch()

def main():
    curses.wrapper(snake_game)

if __name__ == "__main__":
    main()
