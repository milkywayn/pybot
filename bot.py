import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

#bot起動時にコマンド登録
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    # スラッシュコマンド同期
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# guild コマンド読み込み
from commands.guild import guild
bot.tree.add_command(guild)

bot.run(TOKEN)
