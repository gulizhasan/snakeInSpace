use crossterm::{
    event::{self, KeyCode, KeyEvent},
    execute,
    terminal::{self, EnterAlternateScreen, LeaveAlternateScreen},
};
use std::io::{self, Write};
use std::{error::Error, thread, time::Duration};
use tui::layout::Rect;
use tui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction as TuiDirection, Layout},
    style::{Color, Style},
    text::{Span, Spans},
    widgets::{Block, Borders, Paragraph},
    Terminal,
};

#[derive(Clone, Copy)]
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

#[derive(Clone, Copy, PartialEq, Debug)]
struct Point {
    x: i32,
    y: i32,
}

#[derive(Clone)]
struct Snake {
    body: Vec<Point>,
    direction: Direction,
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

    fn move_forward(&mut self) {
        let head = self.body[0];
        let new_head = match self.direction {
            Direction::Up => Point {
                x: head.x,
                y: head.y - 1,
            },
            Direction::Down => Point {
                x: head.x,
                y: head.y + 1,
            },
            Direction::Left => Point {
                x: head.x - 1,
                y: head.y,
            },
            Direction::Right => Point {
                x: head.x + 1,
                y: head.y,
            },
        };

        // Check if the new head is out of bounds before moving.
        if new_head.x >= 1 && new_head.y >= 1 {
            // Adjust the bounds to start from 1
            self.body.insert(0, new_head);
            // Remove the last segment of the snake's body to simulate movement
            self.body.pop();
        } else {
            // Handle collision with the wall or boundary here.
            // For now, let's just exit the game.
            return;
        }
    }

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

fn main() -> Result<(), Box<dyn Error>> {
    let mut stdout = io::stdout();

    {
        let _enter = EnterAlternateScreen;
        execute!(stdout, _enter)?;
    }

    terminal::enable_raw_mode()?;

    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let mut snake = Snake::new();

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
                    KeyCode::Up => snake.change_direction(Direction::Up),
                    KeyCode::Down => snake.change_direction(Direction::Down),
                    KeyCode::Left => snake.change_direction(Direction::Left),
                    KeyCode::Right => snake.change_direction(Direction::Right),
                    KeyCode::Esc | KeyCode::Char('q') => break 'game_loop,
                    _ => {}
                }
            }
        }

        snake.move_forward();

        terminal.draw(|mut f| {
            let chunks = Layout::default()
                .direction(TuiDirection::Vertical)
                .constraints([Constraint::Percentage(100)].as_ref())
                .split(f.size());

            for y in 0..f.size().height {
                for x in 0..f.size().width {
                    let rect = Rect::new(x as u16, y as u16, 1, 1);
                    if x == 0 || x == f.size().width - 1 || y == 0 || y == f.size().height - 1 {
                        // Use 'X' instead of the default border characters
                        f.render_widget(Block::default().borders(Borders::ALL).title("X"), rect);
                    }
                }
            }

            // Render the snake after drawing the borders
            for p in &snake.body {
                let rect = Rect::new((p.x + 1) as u16, (p.y + 1) as u16, 1, 1);
                // Render each segment of the snake with a visible style
                let snake_segment = Paragraph::new(Spans::from(Span::styled(
                    "O",
                    Style::default().fg(Color::White),
                )));
                f.render_widget(snake_segment, rect);
            }
        })?;

        thread::sleep(Duration::from_millis(200));
    }

    terminal::disable_raw_mode()?;

    {
        let _leave = LeaveAlternateScreen;
        execute!(io::stdout(), _leave)?;
    }

    Ok(())
}
