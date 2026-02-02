# commands/guild.py
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

from utils.cache import TTLCache

GUILD_CACHE = TTLCache(ttl=60)
WAR_CACHE = TTLCache(ttl=60)


class Guild(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="guild", description="Show Wynncraft guild info")
    @app_commands.describe(prefix="Guild prefix (e.g. TA)")
    async def guild(self, interaction: discord.Interaction, prefix: str):
        await interaction.response.defer()

        cache_data = GUILD_CACHE.get(prefix)
        if not cache_data:
            cache_data = await self.fetch_guild_data(prefix)
            if not cache_data:
                await interaction.followup.send("❌ ギルド取得に失敗しました")
                return
            GUILD_CACHE.set(prefix, cache_data)

        g, online_by_rank, online_count, total_members = cache_data

        # Owner
        owner_data = g["members"].get("owner", {})
        owner_name = next(iter(owner_data), "Unknown")
        owner_info = owner_data.get(owner_name, {})
        owner_text = (
            f"{owner_name} ({owner_info.get('server')})"
            if owner_info.get("server")
            else owner_name
        )

        # オンライン表示
        online_text = ""
        for rank, players in online_by_rank.items():
            if not players:
                continue

            online_text += f"**{rank.upper()}**\n"

            for p in players:
                wars = p["wars"]
                wars_text = f"**{wars} wars**" if wars >= 1000 else f"{wars} wars"
                safe_name = f"`{p['name']}`"  # _ 無効化

                online_text += f"{safe_name} ({p['server']} | {wars_text})\n"

            online_text += "\n"

        if not online_text:
            online_text = "なし"

        embed = discord.Embed(
            title=f"{g['name']} [{g['prefix']}]",
            color=0x00BFFF
        )

        embed.add_field(
            name="<:crown:1467582546014638100> Owner",
            value=owner_text,
            inline=True
        )
        embed.add_field(
            name="<:poteti:1467555934199873680> Level",
            value=f"{g['level']} [{g['xpPercent']}%]",
            inline=True
        )
        embed.add_field(
            name="<:territory:1467579386856476803> Territories",
            value=str(g["territories"]),
            inline=True
        )
        embed.add_field(
            name="⚔️ Wars",
            value=str(g["wars"]),
            inline=True
        )
        embed.add_field(
            name=f"🟢 Online Members : {online_count}/{total_members}",
            value=online_text,
            inline=False
        )

        embed.set_footer(text="Data from Wynncraft API")

        await interaction.followup.send(embed=embed)

    async def fetch_guild_data(self, prefix: str):
        url = f"https://api.wynncraft.com/v3/guild/prefix/{prefix}"

        async with aiohttp.ClientSession(
            headers={"User-Agent": "DiscordBot/1.0"}
        ) as session:
            async with session.get(url) as res:
                if res.status != 200:
                    return None
                g = await res.json()

        members = g.get("members")
        if not members:
            return None

        online_by_rank = {
            "owner": [],
            "chief": [],
            "strategist": [],
            "captain": [],
            "recruiter": [],
            "recruit": []
        }

        total_members = 0
        online_count = 0

        for rank, users in members.items():
            for name, data in users.items():
                total_members += 1
                if data.get("online"):
                    online_count += 1
                    online_by_rank[rank].append({
                        "name": name,
                        "server": data.get("server", "?")
                    })

        online_list = sum(online_by_rank.values(), [])[:15]

        for p in online_list:
            p["wars"] = await self.fetch_player_wars(p["name"])

        return g, online_by_rank, online_count, total_members

    async def fetch_player_wars(self, name: str) -> int:
        cached = WAR_CACHE.get(name)
        if cached is not None:
            return cached

        url = f"https://api.wynncraft.com/v3/player/{name}"

        async with aiohttp.ClientSession(
            headers={"User-Agent": "DiscordBot/1.0"}
        ) as session:
            async with session.get(url) as res:
                if res.status != 200:
                    return 0
                data = await res.json()

        wars = data.get("globalData", {}).get("wars", 0)
        WAR_CACHE.set(name, wars)
        return wars


async def setup(bot: commands.Bot):
    await bot.add_cog(Guild(bot))
