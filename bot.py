import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Slash Command 同期
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

bot.run(TOKEN)
