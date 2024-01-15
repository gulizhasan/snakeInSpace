#include <iostream>
#include <vector>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <stdlib.h> // For random number generation
#include <time.h>   // For seeding the random number generator

using namespace std;

class Point
{
public:
    int x, y;
    Point(int x, int y) : x(x), y(y) {}
};

class Meteor
{
public:
    Point position;
    Meteor(int x, int y) : position(x, y) {}
};

class Food
{
public:
    Point position;
    Food() : position(-1, -1) {}
    Food(int x, int y) : position(x, y) {}
};

class Portal
{
public:
    Point position;
    bool isActive;
    Portal() : position(-1, -1), isActive(false) {}
    Portal(int x, int y) : position(x, y), isActive(true) {}
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

    bool checkSelfCollision()
    {
        Point head = body.front();
        for (size_t i = 1; i < body.size(); ++i)
        {
            if (head.x == body[i].x && head.y == body[i].y)
            {
                return true; // Collision detected
            }
        }
        return false;
    }

    void grow()
    {
        body.push_back(body.back()); // Add a new segment at the tail
    }

    bool eatsFood(const Point &foodPos)
    {
        if (body.front().x == foodPos.x && body.front().y == foodPos.y)
        {
            grow();
            return true;
        }
        return false;
    }

    void teleportSnake(const Point &newPosition)
    {
        Point tail = body.back();
        int deltaX = newPosition.x - tail.x;
        int deltaY = newPosition.y - tail.y;

        // Shift the entire snake body to the new position
        for (auto &segment : body)
        {
            segment.x += deltaX;
            segment.y += deltaY;
        }
    }

    void move(Portal &portal1, Portal &portal2)
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

        // Check if the snake's head is at a portal
        if (portal1.isActive && head.x == portal1.position.x && head.y == portal1.position.y)
        {
            teleportSnake(portal2.position);
            portal1.isActive = false; // Deactivate the portal after use
            portal2.isActive = false; // Also deactivate the exit portal
        }
        else if (portal2.isActive && head.x == portal2.position.x && head.y == portal2.position.y)
        {
            teleportSnake(portal1.position);
            portal1.isActive = false; // Also deactivate the exit portal
            portal2.isActive = false; // Deactivate the portal after use
        }
        else
        {
            body.insert(body.begin(), head);
            body.pop_back();
        }
    }

    bool isSnakeAtPosition(const Point &position) const
    {
        return body.front().x == position.x && body.front().y == position.y;
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
    Food food;
    int width, height;
    int score;
    vector<Meteor> meteors; // Store meteor positions
    Portal portal1, portal2;
    time_t lastPortalGenerationTime;

    void generatePortals()
    {
        portal1 = generatePortal();
        portal2 = generatePortal();
        lastPortalGenerationTime = time(NULL);
    }

    Portal generatePortal()
    {
        int x, y;
        do
        {
            x = 1 + rand() % (width - 2);
            y = 1 + rand() % (height - 2);
        } while (isSnakePosition(x, y) || isMeteorPosition(x, y));
        return Portal(x, y);
    }

    void checkAndRegeneratePortals()
    {
        if (difftime(time(NULL), lastPortalGenerationTime) >= 30)
        {
            generatePortals();
        }
    }

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

    bool isMeteorPosition(int x, int y) const
    {
        for (const Meteor &meteor : meteors)
        {
            if (meteor.position.x == x && meteor.position.y == y)
            {
                return true;
            }
        }
        return false;
    }

    // Helper function to move the cursor to a specific position in the console
    void gotoxy(int x, int y)
    {
        printf("\033[%d;%dH", y + 1, x + 1);
    }

    void draw()
    {
        clearScreen();

        std::string scoreStr = " Score: " + std::to_string(score) + " ";
        int scoreStartPos = width - scoreStr.length() - 1; // Calculate where to start printing the score

        for (int y = 0; y < height; ++y)
        {
            for (int x = 0; x < width; ++x)
            {
                // Check if we are at the top row where the score should be printed
                if (y == 0 && x >= scoreStartPos && x < width - 1)
                {
                    cout << scoreStr[x - scoreStartPos];
                }
                else if (y == 0 || y == height - 1 || x == 0 || x == width - 1)
                {
                    cout << "X"; // Border
                }
                else if (isSnakePosition(x, y))
                {
                    cout << "O"; // Snake
                }
                else if (isMeteorPosition(x, y))
                {
                    cout << "\033[31m*\033[0m"; // Red meteor
                }
                else if (x == food.position.x && y == food.position.y)
                {
                    cout << "\u03C0"; // Pi symbol for food
                }
                else if (portal1.isActive && x == portal1.position.x && y == portal1.position.y)
                {
                    cout << "\033[34m@\033[0m"; // Blue portal 1
                }
                else if (portal2.isActive && x == portal2.position.x && y == portal2.position.y)
                {
                    cout << "\033[34m@\033[0m"; // Blue portal 2
                }
                else
                {
                    cout << " "; // Empty space
                }
            }
            cout << endl;
        }
    }

    bool
    isSnakePosition(int x, int y) const
    {
        for (const Point &p : snake.getBody())
        {
            if (p.x == x && p.y == y)
                return true;
        }
        return false;
    }

    void generateMeteors(int numMeteors)
    {
        srand(time(NULL)); // Seed the random number generator
        while (meteors.size() < numMeteors)
        {
            int x = rand() % width;
            int y = rand() % height;
            // Ensure meteors do not spawn on the border or on the snake
            if (!isSnakePosition(x, y) && x > 0 && x < width - 1 && y > 0 && y < height - 1)
            {
                meteors.push_back(Meteor(x, y));
            }
        }
    }

    void generateFood()
    {
        int x, y;
        do
        {
            // Generate positions from 1 to width - 2 and 1 to height - 2 to avoid borders
            x = 1 + rand() % (width - 2);
            y = 1 + rand() % (height - 2);
        } while (isSnakePosition(x, y) || isMeteorPosition(x, y));

        food = Food(x, y);
    }

    bool checkMeteorCollision()
    {
        Point head = snake.getBody().front();
        for (const Meteor &meteor : meteors)
        {
            if (meteor.position.x == head.x && meteor.position.y == head.y)
            {
                return true;
            }
        }
        return false;
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

public:
    Game(int width, int height) : width(width), height(height), snake(), score(0), lastPortalGenerationTime(time(NULL))
    {
        // Initialise game
        srand(20049623);    // Easter egg
        getTerminalSize();  // Get the terminal size
        snake = Snake(3);   // Initialise the snake
        generateMeteors(5); // Generate some meteors at the start of the game
        generatePortals();  // Generate initial portals
    }

    void run()
    {
        generateFood(); // Generate initial food

        while (true)
        {
            draw();
            usleep(200000); // Slow down the game loop for visibility

            if (kbhit()) // Input handling
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

            snake.move(portal1, portal2);
            checkAndRegeneratePortals(); // Check if it's time to regenerate portals

            if (snake.eatsFood(food.position))
            {
                score++;        // Increase the score
                generateFood(); // Generate new food
            }

            // Check for collision with the border
            if (snake.checkCollision(width, height))
            {
                cout << "Game Over - Border Collision!" << endl;
                break; // Exit the game loop
            }

            // Check for collision with self
            if (snake.checkCollision(width, height) || snake.checkSelfCollision())
            {
                cout << "Game Over - Collision Detected!" << endl;
                break; // Exit the game loop
            }

            // Check for collision with meteors
            if (checkMeteorCollision())
            {
                cout << "Game Over - Meteor Collision!" << endl;
                break; // Exit the game loop
            }

            cout << "Score: " << score << endl; // Display the score after each draw
        }
    }
};

int main()
{
    Game game(20, 20);
    game.run();
    return 0;
}
