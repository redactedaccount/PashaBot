import os

import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv

# Loading dotenv
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Initializing bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


def insert_movie(input_string):

    movie_type, movie_title = input_string.split(": ", 1)
    conn = sqlite3.connect('pasha.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movies
                 (movie_id INTEGER PRIMARY KEY, movie_type TEXT, movie_title TEXT)''')
    c.execute('INSERT INTO movies (movie_type, movie_title) VALUES (?, ?)', (movie_type, movie_title))
    conn.commit()
    conn.close()


def list_movies_as_discord_modal():
    conn = sqlite3.connect('pasha.db')
    c = conn.cursor()
    c.execute('SELECT movie_id, movie_type, movie_title FROM movies')
    movies = c.fetchall()
    conn.close()
    modal_content = "```"
    for movie_id, movie_type, movie_title in movies:
        modal_content += f"{movie_id}. {movie_type}: {movie_title}\n"
    modal_content += "```"
    return modal_content


@bot.command(name='addmovie', help='Adds a movie to the database. Format: !addmovie A: Movie Title')
async def add_movie(ctx, *, arg):
    insert_movie(arg)
    await ctx.send('Movie added successfully!')


@bot.command(name='listmovies', help='Lists all movies in the database.')
async def list_movies(ctx):
    modal_content = list_movies_as_discord_modal()
    await ctx.send(modal_content)


@bot.command(name='randommovie', help='Selects a random movie of the given type. Format: !randommovie A')
async def random_movie(ctx, movie_type: str):
    if movie_type not in ['A', 'B']:
        await ctx.send('Please specify a valid movie type: A or B.')
        return

    conn = sqlite3.connect('pasha.db')
    c = conn.cursor()
    c.execute('SELECT movie_title FROM movies WHERE movie_type = ? ORDER BY RANDOM() LIMIT 1', (movie_type,))
    movie = c.fetchone()
    conn.close()

    if movie:
        await ctx.send(f"Random {movie_type} movie: {movie[0]}")
    else:
        await ctx.send(f"No movies found for type {movie_type}.")


# API key goes here
bot.run(token)

