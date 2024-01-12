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
        w.addstr(sh//2, sw//2 - len("Game Over! Score: ")//2, "Game Over! Score: {}".format(score))
        w.refresh()
        w.getch()
    except Exception as e:
        # If there's an error, print it to the terminal
        stdscr.clear()
        print("An error occurred while displaying the score: " + str(e))  # Debugging print
        stdscr.addstr(0, 0, "An error occurred: " + str(e))
        stdscr.refresh()
        stdscr.getch()

def main():
    curses.wrapper(snake_game)

if __name__ == "__main__":
    main()
