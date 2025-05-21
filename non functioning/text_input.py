import discord
from discord.ext import commands
import sqlite3  # Example: Using SQLite

# Database setup (Adapt this to your database)
conn = sqlite3.connect('archetypes.db')  # Replace with your database file/connection
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS user_archetypes
                    (user_id INTEGER PRIMARY KEY, archetype TEXT)''')
conn.commit()


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def archetype(ctx):
    """Prompts the user for their archetype and saves it to the database."""

    await ctx.send("What is your character archetype?")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        message = await bot.wait_for('message', check=check, timeout=30)
        archetype = message.content

        # Store the archetype in the database
        user_id = ctx.author.id
        cursor.execute("INSERT OR REPLACE INTO user_archetypes (user_id, archetype) VALUES (?, ?)", (user_id, archetype))
        conn.commit()


        await ctx.send(f"Archetype '{archetype}' saved for user {ctx.author.name}.")

    except TimeoutError:
        await ctx.send("You took too long to respond. Please try again.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

bot.run('YOUR_BOT_TOKEN') # Replace 'YOUR_BOT_TOKEN' with your actual bot token

