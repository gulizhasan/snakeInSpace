import random
import curses

def create_food(snake, window, sh, sw):
    food = None
    while food is None:
        food = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
        if food in snake:
            food = None
    window.addch(food[0], food[1], curses.ACS_PI)
    return food

def snake_game(stdscr):
    curses.curs_set(0)  # Hide the cursor
    sh, sw = stdscr.getmaxyx()  # Get the window's height and width
    w = curses.newwin(sh, sw, 0, 0)  # Create a new window for the game
    w.keypad(1)  # Enable keypad input
    w.timeout(100)  # Set the screen timeout

    # Initialize the snake's initial position and direction
    snake_x = sw//4
    snake_y = sh//2
    snake = [
        [snake_y, snake_x],
        [snake_y, snake_x-1],
        [snake_y, snake_x-2]
    ]
    food = create_food(snake, w, sh, sw)
    w.addch(food[0], food[1], curses.ACS_PI)

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

        # Check for collisions with the border
        if snake[0][0] in [1, sh-2] or snake[0][1]  in [1, sw-2] or snake[0] in snake[1:]:
            break

        try:
            # Draw the new head of the snake
            w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
        except:
            break  # In case the snake tries to go outside the bounds

    stdscr.addstr(sh//2, sw//2, "Game Over! Score: {}".format(score))
    stdscr.refresh()
    stdscr.getch()

def main():
    curses.wrapper(snake_game)

if __name__ == "__main__":
    main()
