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
            window.addch(meteor[0], meteor[1], '*',
                         curses.color_pair(1))  # Use the color pair
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
    curses.start_color()  # Start color functionality

    # Define colours
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # For meteors
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)  # For portals

    curses.curs_set(0)  # Hide the cursor
    sh, sw = stdscr.getmaxyx()  # Get the window's height and width
    w = curses.newwin(sh, sw, 0, 0)  # Create a new window for the game

    # Initialize an empty list for active portals
    active_portals = []

    # Additional variable to track the deactivated portal
    deactivated_portal = None

    w.keypad(1)  # Enable keypad input
    w.timeout(100)  # Set the screen timeout

    # Draw borders using 'X' characters, but avoid the bottom-right corner
    for x in range(sw - 1):  # Adjusted to avoid the last column
        w.addch(0, x, 'X')
        w.addch(sh - 1, x, 'X')
    for y in range(1, sh - 1):  # Start from 1 to avoid overwriting and go up to sh - 1
        w.addch(y, 0, 'X')
        w.addch(y, sw - 1, 'X')

    # Initialize timer for portals
    last_portal_time = time.time()

    # Initialize the snake's initial position and direction
    snake_x = sw//4
    snake_y = sh//2
    snake = [
        [snake_y, snake_x],
        [snake_y, snake_x-1],
        [snake_y, snake_x-2]
    ]

    # Generate food
    food = create_food(snake, w, sh, sw)
    w.addch(food[0], food[1], curses.ACS_PI)

    # Generate meteors
    meteors = create_meteors(snake, food, w, sh, sw)

    # Generate initial portals and add them to active_portals
    portals = create_portals(snake, food, meteors, w, sh, sw)
    active_portals = portals.copy()
    for portal in portals:
        w.addch(portal[0], portal[1], 'O', curses.color_pair(2))

    key = curses.KEY_RIGHT  # Start by moving the snake to the right

    score = 0

    while True:
        next_key = w.getch()
        key = key if next_key == -1 else next_key

        # Determine the new head of the snake based on the key direction
        if key == curses.KEY_DOWN:
            new_head = [snake[0][0]+1, snake[0][1]]
        elif key == curses.KEY_UP:
            new_head = [snake[0][0]-1, snake[0][1]]
        elif key == curses.KEY_LEFT:
            new_head = [snake[0][0], snake[0][1]-1]
        elif key == curses.KEY_RIGHT:
            new_head = [snake[0][0], snake[0][1]+1]

        # Insert the new head of the snake
        snake.insert(0, new_head)

        # Check if snake has eaten the food
        if snake[0] == food:
            score += 1
            food = create_food(snake, w, sh, sw)
            w.addch(food[0], food[1], curses.ACS_PI)
        else:
            # Move the snake by removing the tail
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        # Teleportation logic
        if snake[0] in active_portals and snake[0] != deactivated_portal:
            exit_portal = active_portals[1] if snake[0] == active_portals[0] else active_portals[0]
            snake.insert(0, [exit_portal[0], exit_portal[1]])
            # Deactivate the exit portal temporarily
            deactivated_portal = exit_portal

        # Check if the snake has moved away from the deactivated portal
        if deactivated_portal and snake[0] != deactivated_portal:
            deactivated_portal = None  # Reactivate the portal

        # Regenerate portals every 30 seconds
        current_time = time.time()
        if current_time - last_portal_time >= 30:
            # Clear old portals and update active_portals
            for portal in active_portals:
                w.addch(portal[0], portal[1], ' ')
            portals = create_portals(snake, food, meteors, w, sh, sw)
            active_portals = portals.copy()
            for portal in portals:
                w.addch(portal[0], portal[1], 'O', curses.color_pair(2))
            last_portal_time = current_time

        # Check for collisions with the border
        if snake[0][0] == 0 or snake[0][0] == sh-1 or snake[0][1] == 0 or snake[0][1] == sw-1:
            print("Collision with border detected.")  # Debugging print
            print("Game Over! Score: {}".format(score))  # Debugging print
            time.sleep(5)  # Wait for 5 seconds before breaking
            break

        # Check for collision with itself
        if snake[0] in snake[1:]:
            print("Collision with self detected.")  # Debugging print
            print("Game Over! Score: {}".format(score))  # Debugging print
            time.sleep(5)  # Wait for 5 seconds before breaking
            break

        # Check for collision with a meteor
        if snake[0] in meteors:
            print("Collision with meteor detected.")  # Debugging print
            print("Game Over! Score: {}".format(score))  # Debugging print
            time.sleep(5)  # Wait for 5 seconds before breaking
            break

        try:
            # Draw the new head of the snake
            w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
        except:
            break  # In case the snake tries to go outside the bounds

    # Debugging: Print a message to indicate we're out of the game loop
    print("Exited game loop, attempting to display score.")

    # Ensure the message is printed within the window and the window is refreshed
    try:
        # Clear the window and print the game over message with the score
        w.clear()
        w.addstr(sh//2, sw//2 - len("Game Over! Score: ") //
                 2, "Game Over! Score: {}".format(score))
        w.refresh()
        w.getch()
    except Exception as e:
        # If there's an error, print it to the terminal
        stdscr.clear()
        # Debugging print
        print("An error occurred while displaying the score: " + str(e))
        stdscr.addstr(0, 0, "An error occurred: " + str(e))
        stdscr.refresh()
        stdscr.getch()


def main():
    curses.wrapper(snake_game)


if __name__ == "__main__":
    main()
