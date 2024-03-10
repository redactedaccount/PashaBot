# PashaBot

A work in progress discord bot. Currently just manages a movie suggestion database with two categories (A and B) that 
designate 'Active Watching' and 'Passive Watching'

## Features

**Random Movie Selection**: Chooses a random movie to watch, for active or passive watching.

Type !commands to see a list of commands


## Requirements

- Python 3.6+
- discord.py
- SQLite3
- dotenv
- Loguru for logging

## Installation

1. Clone this repository or download the source code.
2. Install the required Python packages using pip:

`pip install -r requirements.txt`

3. Create a `.env` file in the root directory and add your Discord bot token (Ask Mantisek for the token):

`DISCORD_TOKEN=your_discord_bot_token_here`

4. Run the bot:

`python main.py`

The bot will create a SQLite database when the first movie is added.

## Usage

After inviting the bot to your Discord server and ensuring it has the necessary permissions, you can use the following commands:

- `!addmovie [A or B]: [Movie Name]`: Adds a movie to the database.
- `!listmovies`: Lists all movies in the database.
- `!randommovie [A or B]`: Chooses a random movie from the A or B list.
- `!status`: Shows basic status information about the bot.
- `!commands`: Displays a list of all available commands.

## Configuration

- The bot's command prefix and the movie channel name can be configured in the `main.py` file.
- Logging settings can be adjusted in the `main.py` file using Loguru's configuration options.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.

## License

This project is open-source and available under the MIT License.
