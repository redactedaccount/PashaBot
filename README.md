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

3. Create a `.env` file in the root directory and add your Discord bot token:

`DISCORD_TOKEN=your_discord_bot_token_here`

4. Run the bot:

`python main.py`

The bot will create a SQLite database when the first movie is added.

## Usage

After inviting the bot to your Discord server and ensuring it has the necessary permissions, you can use the following commands:

- `!addmovie [A, B or AB]: [Movie Name]`: Adds a movie to the database. 'AB' adds the movie to both lists.
- `!listmovies [A or B] {Page Number}`: Lists all movies in the database.
- `!randommovie [A or B]`: Chooses a random movie from the A or B list. Either option will also select 'AB' movies.
- `!status`: Shows basic status information about the bot.
- `!commands`: Displays a list of all available commands.

## Configuration

### Environment variables

This project uses `dotenv`

`DISCORD_TOKEN` = Your bot's token

`MOVIENIGHT_CHANNEL` = Normally the default channel is 'movie-night' but you can set it to something different with this.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.


