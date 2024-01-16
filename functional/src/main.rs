use crossterm::{
    terminal::{self, Clear, ClearType},
    ExecutableCommand,
};
use std::io::{stdout, Write};

fn main() {
    let mut stdout = stdout();

    // Clear the terminal
    stdout.execute(Clear(ClearType::All)).unwrap();

    // Get the size of the terminal
    if let Ok((width, height)) = terminal::size() {
        // Draw top and bottom borders
        for _i in 0..width {
            print!("X");
        }
        println!();

        // Draw side borders
        for _ in 2..height {
            println!("X{:width$}X", "", width = (width - 2) as usize);
        }

        // Draw bottom border
        for _i in 0..width {
            print!("X");
        }
        println!();
    }

    // Flush the stdout buffer to ensure everything is printed
    stdout.flush().unwrap();
}

