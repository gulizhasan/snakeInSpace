import random
import curses
import time


def create_food(snake, window, sh, sw):
    food = None
    while food is None:
        food = [random.randint(1, sh - 2), random.randint(1, sw - 3)]
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
        portal = [random.randint(1, sh - 2), random.randint(1, sw - 3)]
        if (portal not in snake and portal != food and portal not in meteors and
                all(1 < p < sh - 2 and 1 < q < sw - 3 for p, q in portals)):
            portals.append(portal)
    return portals


def change_direction(key, current_direction):
    opposite_directions = {'up': curses.KEY_DOWN, 'down': curses.KEY_UP,
                           'left': curses.KEY_RIGHT, 'right': curses.KEY_LEFT}
    # Check if the new key press is not the opposite of the current direction
    if key != opposite_directions[current_direction]:
        return key
    return None


def snake_game(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)

    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)

    initial_speed = 150  # Starting timeout value, set to a slower speed
    speed_increase_interval = 5  # Increase speed when score is a multiple of 5
    speed_increase_amount = 10  # Amount by which speed increases
    max_speed = 50  # Maximum speed limit
    current_speed = initial_speed
    speed_updated_at_score = 0  # To track when the speed was last updated

    w.timeout(current_speed)  # Set initial speed

    score = 0
    last_score_update = 0  # To track when the last speed update happened

    snake_x = sw//4
    snake_y = sh//2
    snake = [[snake_y, snake_x], [snake_y, snake_x-1], [snake_y, snake_x-2]]

    food = create_food(snake, w, sh, sw)
    w.addch(food[0], food[1], curses.ACS_PI)

    meteors = create_meteors(snake, food, w, sh, sw)

    # Generate the initial pair of portals
    portals = create_portals(snake, food, meteors, w, sh, sw)
    for portal in portals:
        w.addch(portal[0], portal[1], '@', curses.color_pair(2))

    # Variables to track last portal used and time since last portal use
    last_portal_used_time = 0
    last_portal_time = time.time()  # Initialise the variable to the current time

    key = curses.KEY_RIGHT
    current_direction = 'right'  # Initialize the current direction

    # Draw borders using 'X' characters, adjusted to stay within window bounds
    for y in range(sh):
        w.addch(y, 0, 'X')
        w.addch(y, sw - 2, 'X')
    for x in range(sw - 1):
        w.addch(0, x, 'X')
        w.addch(sh - 1, x, 'X')

    vertical_speed_adjustment = 2  # Slow down vertical movement
    easter_egg_triggered = False  # Easter egg condition

    while True:
        next_key = w.getch()
        if next_key != -1:
            new_direction = change_direction(next_key, current_direction)
            if new_direction:
                key = new_direction
                current_direction = {curses.KEY_DOWN: 'down', curses.KEY_UP: 'up',
                                     curses.KEY_LEFT: 'left', curses.KEY_RIGHT: 'right'}[key]

        new_head = [snake[0][0], snake[0][1]]

        if key == curses.KEY_DOWN:
            new_head[0] += 1
            # Slow down when moving down
            w.timeout(current_speed * vertical_speed_adjustment)
        elif key == curses.KEY_UP:
            new_head[0] -= 1
            # Slow down when moving up
            w.timeout(current_speed * vertical_speed_adjustment)
        elif key == curses.KEY_LEFT:
            new_head[1] -= 1
            w.timeout(current_speed)  # Normal speed when moving left
        elif key == curses.KEY_RIGHT:
            new_head[1] += 1
            w.timeout(current_speed)  # Normal speed when moving right

        # Self-collision detection
        if new_head in snake:
            break

        snake.insert(0, new_head)

        if snake[0] == food:
            score += 1
            food = create_food(snake, w, sh, sw)
            w.addch(food[0], food[1], curses.ACS_PI)

            # Update speed if score is a multiple of 5 and hasn't been updated for this score
            if score % speed_increase_interval == 0 and score != speed_updated_at_score:
                current_speed = max(
                    current_speed - speed_increase_amount, max_speed)
                w.timeout(current_speed)
                speed_updated_at_score = score
        else:
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        # Check for Easter egg condition
        if score == 10 and not easter_egg_triggered:
            easter_egg_triggered = True
            w.addstr(1, sw//2 - len("Easter Egg: 20049623")//2,
                     "Easter Egg: 20049623", curses.color_pair(2))

        # Portal logic
        portal_used = False
        for portal in portals:
            if snake[0] == portal and time.time() - last_portal_used_time > 1:
                exit_portal = portals[1] if snake[0] == portals[0] else portals[0]
                snake.insert(0, [exit_portal[0], exit_portal[1]])
                last_portal_used_time = time.time()
                portal_used = True
                break

        # Regenerate portals every 30 seconds and only if there's one pair on screen
        current_time = time.time()
        if current_time - last_portal_time >= 30:
            # Clear old portals and generate new ones
            for portal in portals:
                w.addch(portal[0], portal[1], ' ')
            portals = create_portals(snake, food, meteors, w, sh, sw)
            for portal in portals:
                w.addch(portal[0], portal[1], '@', curses.color_pair(2))
            last_portal_time = current_time

        # Border collision detection
        if (snake[0][0] == 0 or snake[0][0] == sh - 1 or
                snake[0][1] == 0 or snake[0][1] == sw - 2):  # Updated to sw - 2
            break

        # Meteor collision detection
        if snake[0] in meteors:
            break

        # Redraw snake and score
        try:
            w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
        except:
            break

        score_str = f"Score: {score}"
        w.addstr(0, sw - len(score_str) - 2, score_str)

    # Game Over logic
    w.clear()
    game_over_msg = f"Game Over! Score: {score}"
    w.addstr(sh//2, sw//2 - len(game_over_msg)//2, game_over_msg)
    w.refresh()
    time.sleep(2)  # Pause for 2 seconds on the Game Over screen


def main():
    curses.wrapper(snake_game)


if __name__ == "__main__":
    main()
