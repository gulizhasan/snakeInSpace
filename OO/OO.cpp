#include <iostream>
#include <vector>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>

using namespace std;

class Point
{
public:
    int x, y;
    Point(int x, int y) : x(x), y(y) {}
};

class Snake
{
private:
    vector<Point> body;
    char dir;

    bool isValidDirection(char newDir)
    {
        // Prevent the snake from reversing directly into itself
        if ((dir == 'R' && newDir == 'L') || (dir == 'L' && newDir == 'R') ||
            (dir == 'U' && newDir == 'D') || (dir == 'D' && newDir == 'U'))
        {
            return false;
        }
        return true;
    }

public:
    Snake(int initLength = 3)
    {
        // Initialize the snake at the middle of the screen
        for (int i = 0; i < initLength; ++i)
        {
            body.push_back(Point(10, 10 + i));
        }
        dir = 'L'; // Start by moving to the left
    }

    void changeDirection(char newDir)
    {
        if (isValidDirection(newDir))
        {
            dir = newDir;
        }
    }

    bool checkCollision(int width, int height)
    {
        Point head = body.front();
        // Check if the head is at any border
        return head.x <= 0 || head.x >= width - 1 || head.y <= 0 || head.y >= height - 1;
    }

    void move()
    {
        Point head = body.front();
        if (dir == 'U')
            --head.y;
        else if (dir == 'D')
            ++head.y;
        else if (dir == 'L')
            --head.x;
        else if (dir == 'R')
            ++head.x;

        body.insert(body.begin(), head);
        body.pop_back();
    }

    const vector<Point> &getBody() const
    {
        return body;
    }
};

class Game
{
private:
    Snake snake;
    int width, height;

    // Function to get terminal size
    void getTerminalSize()
    {
        struct winsize w;
        ioctl(STDOUT_FILENO, TIOCGWINSZ, &w);
        width = w.ws_col;
        height = w.ws_row - 1; // Subtract one to make the game area one line smaller
    }

    void clearScreen()
    {
        system("clear");
    }

    void draw()
    {
        clearScreen();

        for (int y = 0; y < height; ++y)
        {
            for (int x = 0; x < width; ++x)
            {
                if (y == 0 || y == height - 1 || x == 0 || x == width - 1)
                {
                    cout << "X"; // Border character
                }
                else if (isSnakePosition(x, y))
                {
                    cout << "*"; // Snake character
                }
                else
                {
                    cout << " "; // Empty space
                }
            }
            cout << endl;
        }
    }

    bool isSnakePosition(int x, int y) const
    {
        for (const Point &p : snake.getBody())
        {
            if (p.x == x && p.y == y)
                return true;
        }
        return false;
    }

public:
    Game(int width, int height) : width(width), height(height), snake()
    {
        getTerminalSize(); // Get the terminal size
        snake = Snake(3);  // Initialize the snake
    }

    void run()
    {
        while (true)
        {
            draw();
            usleep(200000); // Slow down the game loop for visibility

            if (kbhit())
            {
                char ch = getchar();
                if (ch == 27) // Arrow keys start with an escape character
                {
                    getchar();      // Skip the '[' character
                    ch = getchar(); // Get the direction character
                    switch (ch)
                    {
                    case 'A':
                        snake.changeDirection('U');
                        break; // Up arrow
                    case 'B':
                        snake.changeDirection('D');
                        break; // Down arrow
                    case 'C':
                        snake.changeDirection('R');
                        break; // Right arrow
                    case 'D':
                        snake.changeDirection('L');
                        break; // Left arrow
                    }
                }
            }
            snake.move();

            if (snake.checkCollision(width, height))
            {
                cout << "Game Over!" << endl;
                break; // Exit the game loop
            }
        }
    }

    bool kbhit()
    {
        termios oldt, newt;
        int ch;
        int oldf;

        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &newt);
        oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
        fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);

        ch = getchar();

        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
        fcntl(STDIN_FILENO, F_SETFL, oldf);

        if (ch != EOF)
        {
            ungetc(ch, stdin);
            return true;
        }

        return false;
    }
};

int main()
{
    Game game(20, 20);
    game.run();
    return 0;
}
