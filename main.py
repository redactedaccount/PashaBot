import os
import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
from datetime import datetime
from loguru import logger

# Configure logger
logger.add("runtime.log", rotation="1 week", level="INFO")

# Get starting time for uptime
start_time = datetime.now()

# Loading dotenv
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Initializing bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration settings
movie_channel = 'movie-night'


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')


def insert_movie(input_string, added_by):
    try:
        movie_type, movie_title = input_string.split(": ", 1)
        added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect('pasha.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS movies
                     (movie_id INTEGER PRIMARY KEY, movie_type TEXT, movie_title TEXT, added_at DATETIME, added_by TEXT)''')
        c.execute('INSERT INTO movies (movie_type, movie_title, added_at, added_by) VALUES (?, ?, ?, ?)',
                  (movie_type, movie_title, added_at, added_by))
        conn.commit()
        logger.info(f'Movie "{movie_title}" added by {added_by}')
    except Exception as e:
        logger.error(f'Error inserting movie: {e}')
    finally:
        conn.close()


def get_movies_list():
    try:
        conn = sqlite3.connect('pasha.db')
        c = conn.cursor()
        c.execute('SELECT movie_id, movie_type, movie_title, added_at, added_by FROM movies')
        movies = c.fetchall()
        conn.close()
        movielist_content = "```"
        for movie_id, movie_type, movie_title, added_at, added_by in movies:
            added_at_datetime = datetime.strptime(added_at, "%Y-%m-%d %H:%M:%S")
            added_at_timestamp = int(added_at_datetime.timestamp())

            movielist_content += f"{movie_id}. {movie_type}: {movie_title} (Added by {added_by} <t:{added_at_timestamp}:R> on <t:{added_at_timestamp}:f>)\n"
        movielist_content += "```"
        return movielist_content
    except Exception as e:
        logger.error(f'Error fetching movies list: {e}')
        return "Failed to fetch movies list due to an error."


@bot.command(name='addmovie', help='Adds a movie to the database. Format: !addmovie A: Movie Title', hidden=True)
async def add_movie(ctx, *, arg):
    if any(char in arg for char in "`'\";"):
        await ctx.send("Used restricted characters. (`'\";). Please remove them and try again.")
        return

    if str(ctx.channel) == movie_channel:
        user = str(ctx.message.author)
        insert_movie(arg, user)
        logger.info(f"'addmovie' command called by {user} with argument: {arg}")
        await ctx.send('Movie added successfully!')
    else:
        logger.info(f"'addmovie' command called outside of movie-night channel by {ctx.message.author}")



@bot.command(name='listmovies', help='Lists all movies in the database.', hidden=True)
async def list_movies_cmd(ctx):
    if str(ctx.channel) == movie_channel:
        try:
            conn = sqlite3.connect('pasha.db')
            c = conn.cursor()
            c.execute('SELECT movie_id, movie_type, movie_title, added_at, added_by FROM movies ORDER BY movie_type')
            movies = c.fetchall()
            conn.close()

            embed = discord.Embed(title="Movie List", description="Movies for movie night:", color=0x00ff00)
            current_type = ''
            movie_list_content = ''

            for movie_id, movie_type, movie_title, added_at, added_by in movies:
                if movie_type != current_type:
                    if current_type:  # Add the previous type's movies to the embed before starting a new type
                        embed.add_field(name=f"Type {current_type} Movies", value=movie_list_content, inline=False)
                        movie_list_content = ''  # Reset the list content for the next type
                    current_type = movie_type

                added_at_datetime = datetime.strptime(added_at, "%Y-%m-%d %H:%M:%S")
                added_at_timestamp = int(added_at_datetime.timestamp())
                movie_info = f"(ID:{movie_id}) {movie_title} (Added by {added_by} <t:{added_at_timestamp}:R> on <t:{added_at_timestamp}:f>)\n"
                movie_list_content += movie_info

            # Add the last type's movies to the embed
            if movie_list_content:
                embed.add_field(name=f"Type {current_type} Movies", value=movie_list_content, inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f'Error fetching movies list: {e}')
            await ctx.send("Failed to fetch movies list due to an error.")
    else:
        logger.info(f"'listmovies' command called outside of movie-night channel by {ctx.message.author}")


@bot.command(name='randommovie', help='Selects a random movie of the given type. Format: !randommovie A', hidden=True)
async def random_movie(ctx, movie_type: str):
    if str(ctx.channel) == movie_channel:
        if movie_type not in ['A', 'B']:
            await ctx.send('Please specify a valid movie type: A or B.')
            return

        conn = sqlite3.connect('pasha.db')
        c = conn.cursor()
        try:
            c.execute('SELECT movie_title FROM movies WHERE movie_type = ? ORDER BY RANDOM() LIMIT 1', (movie_type,))
            movie = c.fetchone()
            if movie:
                await ctx.send(f"Random {movie_type} movie: {movie[0]}")
            else:
                await ctx.send(f"No movies found for type {movie_type}.")
        except Exception as e:
            logger.error(f'Error selecting random movie: {e}')
            await ctx.send('Failed to select a random movie due to an error.')
        finally:
            conn.close()
    else:
        logger.info(f"'randommovie' command called outside of movie-night channel by {ctx.message.author}")


@bot.command(name='status', help='Gets some status information about the bot and what it is doing.', hidden=True)
async def print_status(ctx):
    current_time = datetime.now()
    uptime = current_time - start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    status_string = f"""
```
Movie Channel: {movie_channel}
Uptime: {hours}h {minutes}m {seconds}s
Current Channel: {str(ctx.channel)}
User who called: {str(ctx.message.author)}
```
"""
    await ctx.send(status_string)


@bot.command(name='commands', help='See all available commands.')
async def commands(ctx):
    embed = discord.Embed(title="Commands", description="List of available commands:", color=0x00ff00)
    # Adding commands and their descriptions as fields
    embed.add_field(name="!addmovie [A or B]: [Movie Name]",
                    value="Adds a movie to the A or B list. A is for active watching, B is for passive watching. \n Example: `!addmovie A: The Matrix`",
                    inline=False)
    embed.add_field(name="!listmovies", value="Lists all movies in the database.", inline=False)
    embed.add_field(name="!randommovie [A or B]", value="Chooses a random movie from the A or B list.", inline=False)
    embed.add_field(name="!status", value="Basic status information about the bot.", inline=False)
    # Sending the embed
    await ctx.send(embed=embed)


# Run the bot with the API key
bot.run(token)
