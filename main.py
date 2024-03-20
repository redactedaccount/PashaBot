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
movienight_channel = os.getenv('MOVIENIGHT_CHANNEL')



# Initializing bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration settings
if movienight_channel:
    movie_channel = movienight_channel
    logger.info(f'MOVIENIGHT_CHANNEL env variable used. {movie_channel} selected as Movie Night channel.')
else:
    movie_channel = 'movie-night'
    logger.info(f'MOVIENIGHT_CHANNEL env variable blank. {movie_channel} defaulted to as Movie Night channel.')

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


        for char in movie_type:
            c.execute('INSERT INTO movies (movie_type, movie_title, added_at, added_by) VALUES (?, ?, ?, ?)',
                      (char, movie_title, added_at, added_by))
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

    arg_movie_type = arg.split(':')[0]
    if arg_movie_type not in ['A', 'B', 'AB']:
        await ctx.send("Not a valid movie type.  Use A, B or AB (for both lists)")
        return

    if str(ctx.channel) == movie_channel:
        user = str(ctx.message.author)

        insert_movie(arg, user)
        logger.info(f"'addmovie' command called by {user} with argument: {arg}")
        await ctx.send('Movie added successfully!')
    else:
        logger.info(f"'addmovie' command called outside of movie-night channel by {ctx.message.author}")


import discord
import sqlite3
from datetime import datetime


@bot.command(name='listmovies', help='Lists all movies in the database.', hidden=True)
async def list_movies_cmd(ctx, movie_type: str = None, page_number: int = 1):
    if not movie_type:
        await ctx.send('Select either A or B. Can also select a page. Example: !listmovies A 2 (Will show you the second page of movies)')
        return
    if str(ctx.channel) == movie_channel:
        try:
            # Determine movie type description
            type_description = "Active Watching" if movie_type.upper() == "A" else "Passive Watching" if movie_type.upper() == "B" else None
            if not type_description:
                await ctx.send(
                    "Invalid movie type provided. Please use 'A' for Active Watching or 'B' for Passive Watching.")
                return

            conn = sqlite3.connect('pasha.db')
            c = conn.cursor()
            # Calculate offset for pagination
            offset = (page_number - 1) * 20
            c.execute(
                'SELECT movie_id, movie_title, added_at, added_by FROM movies WHERE 1=1 AND (movie_type = ? OR movie_type = "AB") ORDER BY movie_title LIMIT 20 OFFSET ?',
                (movie_type.upper(), offset))
            movies = c.fetchall()
            conn.close()

            if not movies:
                await ctx.send(f"No movies found for type {type_description} on page {page_number}.")
                return

            embed = discord.Embed(title=f"Movie List - {type_description}",
                                  description=f"Movies for movie night (Page {page_number}):", color=0x00ff00)

            for movie_id, movie_title, added_at, added_by in movies:
                added_at_datetime = datetime.strptime(added_at, "%Y-%m-%d %H:%M:%S")
                added_at_timestamp = int(added_at_datetime.timestamp())
                movie_info = f"(ID:{movie_id}) (Added by {added_by} <t:{added_at_timestamp}:R> on <t:{added_at_timestamp}:f>)"

                embed.add_field(name=movie_title, value=movie_info, inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f'Error fetching movies list: {e}')
            await ctx.send("Failed to fetch movies list due to an error.")
    else:
        logger.info(f"'listmovies' command called outside of movie-night channel by {ctx.message.author}")


@bot.command(name='randommovie', help='Selects a random movie of the given type. Format: !randommovie A', hidden=True)
async def random_movie(ctx, movie_type: str = None):

    if str(ctx.channel) == movie_channel:
        if movie_type not in ['A', 'B']:
            await ctx.send('Please specify a valid movie type: A or B.')
            return

        conn = sqlite3.connect('pasha.db')
        c = conn.cursor()
        try:
            #Setting AB explicitly for now as we don't anticipate adding more movie types.
            c.execute("""
            SELECT 
            movie_title,
            added_by 
            FROM movies 
            WHERE 1=1 
            AND (movie_type = ? OR movie_type = "AB")
            ORDER BY RANDOM() LIMIT 1
            """,(movie_type,))
            movie = c.fetchone()
            if movie:
                await ctx.send(f"Random {movie_type} movie: {movie[0]} (Added by {movie[1]})")
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
    try:
        conn = sqlite3.connect('pasha.db')
        c = conn.cursor()
        # Fetch counts for each category including AB counted in both A and B
        c.execute('''SELECT movie_type, COUNT(*) FROM movies WHERE movie_type IN ('A', 'AB')''')
        count_a = sum([count for type, count in c.fetchall() if type in ['A', 'AB']])
        c.execute('''SELECT movie_type, COUNT(*) FROM movies WHERE movie_type IN ('B', 'AB')''')
        count_b = sum([count for type, count in c.fetchall() if type in ['B', 'AB']])

        pages_a = (count_a + 19) // 20  # +19 for ceiling effect
        pages_b = (count_b + 19) // 20  # +19 for ceiling effect

        conn.close()
    except Exception as e:
        logger.error(f'Error fetching movie counts: {e}')
        count_a = count_b = pages_a = pages_b = 0

    current_time = datetime.now()
    uptime = current_time - start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(title="Pasha Status", description="Current status and statistics:", color=0x00ff00)
    embed.add_field(name="Movie Channel", value=movie_channel, inline=False)
    embed.add_field(name="Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=False)
    embed.add_field(name="Current Channel", value=str(ctx.channel), inline=False)
    embed.add_field(name="User who called", value=str(ctx.message.author), inline=False)
    embed.add_field(name="A-Type Movies", value=f"{count_a} movies ({pages_a} pages)", inline=False)
    embed.add_field(name="B-Type Movies", value=f"{count_b} movies ({pages_b} pages)", inline=False)


    await ctx.send(embed=embed)


@bot.command(name='commands', help='See all available commands.')
async def commands(ctx):
    embed = discord.Embed(title="Commands", description="List of available commands:", color=0x00ff00)
    # Adding commands and their descriptions as fields
    embed.add_field(name="!addmovie [A, B or AB]: [Movie Name]",
                    value="""
                    Adds a movie to the A or B list. A is for active watching, B is for passive watching. \n Example: `!addmovie A: The Matrix`
                    A value of 'AB' will add the movie to both lists for selection.
                    """,
                    inline=False)
    embed.add_field(name="!listmovies", value="Lists all movies by type. Paginated. Defaults to page 1 without a page number. Ex. !listmovies A 2", inline=False)
    embed.add_field(name="!randommovie [A or B]", value="Chooses a random movie from the A or B list.", inline=False)
    embed.add_field(name="!status", value="Basic status information about the bot.", inline=False)
    # Sending the embed
    await ctx.send(embed=embed)


# Run the bot with the API key
bot.run(token)
