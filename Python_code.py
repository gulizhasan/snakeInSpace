import os
import msvcrt  # Only works on Windows
import time

# Game settings
width = 30
height = 20
border_char = "x"
snake_head = "@"
snake_char = "O"
food_char = "*"

# Inital snake position
snake = [(width // 2, height // 2)]
direction = (1, 0)

# Initial food position
food = None


def splash_screen():
    # Clear the console screen
    os.system("cls" if os.name == "nt" else "clear")

    splash_text = """
    * * * * * * * * * * * * * * * * * * * *
    *                                     *
    *                                     *
    *                                     *
    *           Snake: in Space           *
    *       press any key to start        *
    *                                     *
    *                                     *
    *                                     *
    * * * * * * * * * * * * * * * * * * * *
    """

    print(splash_text)


def print_board():
    # Top border
    print((border_char + " ") * (width + 2))

    # Game board
    for x in range(height):
        print(border_char, end=" ")
        for y in range(width):
            if (y, x) == snake[0]:
                print(snake_head, end=" ")
            elif (y, x) in snake[1:]:
                print(snake_char, end=" ")
            elif (y, x) == food:
                print(food_char, end=" ")
            else:
                print(" ", end=" ")
        print(border_char)

    # Bottom border
    print((border_char + " ") * (width + 2))


def move_snake():
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    snake.insert(0, new_head)

    # Check for collision with walls or itself
    if (
        new_head[0] < 0
        or new_head[0] >= width
        or new_head[1] < 0
        or new_head[1] >= height
        or new_head in snake[1:]
    ):
        game_over()


def game_over():
    os.system("cls" if os.name == "nt" else "clear")
    print("GAME OVER")
    exit()

def get_key():
        key = msvcrt.getch()
        return key


def main():
    global direction
    splash_screen()
    get_key()  # wait for keypress

    while msvcrt.kbhit():
        # clear input buffer
        msvcrt.getch()  # wait for keypress

    while True:
        print_board()
        move_snake()

        key= get_key()
        if key == b"w" and direction != (0, 1):
                        direction = (0, -1)  # Move up
        elif key == b"s" and direction != (0, -1):
                        direction = (0, 1)  # Move down
        elif key == b"a" and direction != (1, 0):
                        direction = (-1, 0)  # Move left
        elif key == b"d" and direction != (-1, 0):
                        direction = (1, 0)  # Move right

        # Adjust game speed (you can modify this value)
        time.sleep(0.1)


if __name__ == "__main__":
        main()
