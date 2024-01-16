// Import necessary modules from crossterm and other standard libraries
use crossterm::{
    event::{self, KeyCode, KeyEvent},
    execute,
    terminal::{self, EnterAlternateScreen, LeaveAlternateScreen},
};
use rand::{thread_rng, Rng};
use std::io::{self};
use std::{error::Error, thread, time::Duration};
use tui::layout::Rect;
use tui::{
    backend::CrosstermBackend,
    style::{Color, Style},
    text::{Span, Spans},
    widgets::Paragraph,
    Terminal,
};

// Enumeration to represent the snake's direction
#[derive(Clone, Copy)]
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

// A struct representing a point (or segment) in 2D space
#[derive(Clone, Copy, PartialEq, Debug)]
struct Point {
    x: i32,
    y: i32,
}

// Struct to represent the snake
#[derive(Clone)]
struct Snake {
    body: Vec<Point>,
    direction: Direction,
}

// Struct to represent the food
#[derive(Clone, Copy, PartialEq, Debug)]
struct Food {
    position: Point,
}

// Struct to represent the meteors
#[derive(Clone, Copy, PartialEq, Debug)]
struct Meteor {
    position: Point,
}

// Struct to represent the portals
#[derive(Clone, Copy, PartialEq, Debug)]
struct Portal {
    entry: Point,
    exit: Point,
    active: bool,
}

impl Snake {
    fn new() -> Snake {
        Snake {
            // Initialize the snake with three segments
            body: vec![
                Point { x: 5, y: 5 },
                Point { x: 4, y: 5 },
                Point { x: 3, y: 5 },
            ],
            direction: Direction::Right,
        }
    }

    // Moves the snake in the current direction by adding a new head and removing the tail
    fn move_forward(
        &mut self,
        terminal_size: (u16, u16),
        food_position: Point,
        meteors: &[Meteor],
        portal: &mut Portal,
    ) -> (bool, bool) {
        let head = self.body[0];
        let mut new_head = match self.direction {
            Direction::Up => Point { x: head.x, y: head.y - 1 },
            Direction::Down => Point { x: head.x, y: head.y + 1 },
            Direction::Left => Point { x: head.x - 1, y: head.y },
            Direction::Right => Point { x: head.x + 1, y: head.y },
        };

        // Check for collision with meteors
        if meteors.iter().any(|m| m.position == new_head) {
            return (false, false); // Collision with a meteor
        }

        // Portal teleportation logic
        if portal.active && (new_head == portal.entry || new_head == portal.exit) {
            new_head = if new_head == portal.entry { portal.exit } else { portal.entry };
            portal.active = false; // Deactivate the portal after use
        }

        // Check if the new head is within the terminal bounds
        if new_head.x >= 0
            && new_head.y >= 0
            && new_head.x < terminal_size.0 as i32 - 2
            && new_head.y < terminal_size.1 as i32 - 2
        {
            let ate_food = new_head == food_position; // Check if snake ate the food
            self.body.insert(0, new_head);

            if !ate_food {
                self.body.pop(); // Remove the last segment if food is not eaten
            }

            (true, ate_food) // Return true for successful movement, and whether food was eaten
        } else {
            (false, false) // Return false for collision with wall, and false for food not eaten
        }
    }

    // Changes the snake's direction unless it's directly opposite to current direction
    fn change_direction(&mut self, new_direction: Direction) {
        if !(matches!(
            (self.direction, new_direction),
            (Direction::Up, Direction::Down)
                | (Direction::Down, Direction::Up)
                | (Direction::Left, Direction::Right)
                | (Direction::Right, Direction::Left)
        )) {
            self.direction = new_direction;
        }
    }
}

impl Food {
    fn new(snake: &Snake, terminal_size: (u16, u16)) -> Food {
        let mut rng = thread_rng();
        let (width, height) = terminal_size;
        let mut new_position;

        loop {
            new_position = Point {
                x: rng.gen_range(1..width as i32 - 1),
                y: rng.gen_range(1..height as i32 - 1),
            };
            if !snake.body.contains(&new_position) {
                break;
            }
        }

        Food {
            position: new_position,
        }
    }
}

impl Meteor {
    // Function to generate a new meteor at a random position, avoiding the borders and snake
    fn new(terminal_size: (u16, u16), snake: &Snake) -> Meteor {
        let mut rng = thread_rng();
        let (width, height) = terminal_size;
        let mut new_position;

        loop {
            // Generate positions away from the borders (1 unit inside the actual game area)
            new_position = Point {
                x: rng.gen_range(2..width as i32 - 2), // Adjusted range to avoid borders
                y: rng.gen_range(2..height as i32 - 2), // Adjusted range to avoid borders
            };
            // Ensure the meteor doesn't spawn on the snake
            if !snake.body.contains(&new_position) {
                break;
            }
        }

        Meteor {
            position: new_position,
        }
    }
}

impl Portal {
    // Function to generate a new pair of portals
    fn new(terminal_size: (u16, u16), snake: &Snake) -> Portal {
        let mut rng = thread_rng();
        let (width, height) = terminal_size;
        let mut entry_position;
        let mut exit_position;

        loop {
            entry_position = Point {
                x: rng.gen_range(1..width as i32 - 1),
                y: rng.gen_range(1..height as i32 - 1),
            };
            exit_position = Point {
                x: rng.gen_range(1..width as i32 - 1),
                y: rng.gen_range(1..height as i32 - 1),
            };
            if !snake.body.contains(&entry_position)
                && !snake.body.contains(&exit_position)
                && entry_position != exit_position
            {
                break;
            }
        }

        Portal {
            entry: entry_position,
            exit: exit_position,
            active: true,
        }
    }
}

fn main() -> Result<(), Box<dyn Error>> {
    let mut stdout = io::stdout();

    {
        let _enter = EnterAlternateScreen;
        execute!(stdout, _enter)?;
    }

    // Enable raw mode for the terminal
    terminal::enable_raw_mode()?;

    // Create a backend for the TUI using Crossterm
    let backend = CrosstermBackend::new(stdout);
    // Create a TUI terminal
    let mut terminal = Terminal::new(backend)?;

    // Get terminal size and extract width and height
    let terminal_size = terminal.size()?;
    let terminal_dimensions = (terminal_size.width, terminal_size.height);

    // Define snake before using it to create food
    let mut snake = Snake::new();
    let mut food = Food::new(&snake, terminal_dimensions);

    // Generate a list of static meteors
    let mut meteors = Vec::new();
    for _ in 0..5 {
        // Adjust the number of meteors as needed
        meteors.push(Meteor::new(terminal_dimensions, &snake));
    }

    // Initial portal generation
    let mut portal = Portal::new(terminal_dimensions, &snake);
    let mut last_portal_time = std::time::Instant::now();

    'game_loop: loop {
        if event::poll(Duration::from_millis(100))? {
            if let event::Event::Key(KeyEvent {
                code,
                state,
                modifiers,
                kind,
            }) = event::read()?
            {
                match code {
                    // Handle arrow keys and 'q' key to change direction or quit
                    KeyCode::Up => snake.change_direction(Direction::Up),
                    KeyCode::Down => snake.change_direction(Direction::Down),
                    KeyCode::Left => snake.change_direction(Direction::Left),
                    KeyCode::Right => snake.change_direction(Direction::Right),
                    KeyCode::Esc | KeyCode::Char('q') => break 'game_loop,
                    _ => {}
                }
            }
        }

        let (snake_moved, ate_food) =
            snake.move_forward(terminal_dimensions, food.position, &meteors, &mut portal);

        if !snake_moved {
            // Handle game over due to collision with meteors or border
            break 'game_loop;
        }

        if ate_food {
            food = Food::new(&snake, terminal_dimensions); // Reposition food if eaten
        }

        terminal.draw(|f| {
            let size = f.size();

            // Render the borders with 'X'
            for y in 0..size.height {
                for x in 0..size.width {
                    if x == 0 || x == size.width - 1 || y == 0 || y == size.height - 1 {
                        let rect = Rect::new(x, y, 1, 1);
                        let border_char = Paragraph::new(Spans::from(Span::raw("X")));
                        f.render_widget(border_char, rect);
                    }
                }
            }

            // Render the snake after drawing the borders
            for p in &snake.body {
                let rect = Rect::new((p.x + 1) as u16, (p.y + 1) as u16, 1, 1);
                let snake_segment = Paragraph::new(Spans::from(Span::styled(
                    "O",
                    Style::default().fg(Color::White),
                )));
                f.render_widget(snake_segment, rect);
            }

            // Render the food
            let food_rect = Rect::new(
                (food.position.x + 1) as u16,
                (food.position.y + 1) as u16,
                1,
                1,
            );
            let food_widget = Paragraph::new(Spans::from(Span::styled(
                "\u{03c0}",                        // Pi symbol as food character
                Style::default().fg(Color::White), // Food color
            )));
            f.render_widget(food_widget, food_rect);

            // Render each meteor
            for meteor in &meteors {
                let meteor_rect = Rect::new(
                    (meteor.position.x + 1) as u16,
                    (meteor.position.y + 1) as u16,
                    1,
                    1,
                );
                let meteor_widget = Paragraph::new(Spans::from(Span::styled(
                    "*",                             // Meteor character
                    Style::default().fg(Color::Red), // Meteor color
                )));
                f.render_widget(meteor_widget, meteor_rect);
            }

            // Render portals if active
            if portal.active {
                let entry_rect = Rect::new(
                    (portal.entry.x + 1) as u16,
                    (portal.entry.y + 1) as u16,
                    1,
                    1,
                );
                let exit_rect =
                    Rect::new((portal.exit.x + 1) as u16, (portal.exit.y + 1) as u16, 1, 1);

                let portal_widget = Paragraph::new(Spans::from(Span::styled(
                    "@",
                    Style::default().fg(Color::Blue),
                )));

                f.render_widget(portal_widget.clone(), entry_rect); // Clone for entry
                f.render_widget(portal_widget, exit_rect); // Use original for exit
            }

            // Portal generation logic
            if !portal.active && last_portal_time.elapsed() > Duration::from_secs(30) {
                portal = Portal::new(terminal_dimensions, &snake);
                last_portal_time = std::time::Instant::now();
            }
        })?;

        // Delay to control the speed of the game
        thread::sleep(Duration::from_millis(200));
    }

    // Disable raw mode and leave the alternate screen
    terminal::disable_raw_mode()?;

    {
        let _leave = LeaveAlternateScreen;
        execute!(io::stdout(), _leave)?;
    }

    Ok(())
}
