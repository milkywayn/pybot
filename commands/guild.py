import discord
from discord import app_commands
from utils.cache import fetch_guild_data


@app_commands.command(
    name="guild",
    description="Wynncraft guild info"
)
@app_commands.describe(prefix="Guild prefix")
async def guild(interaction: discord.Interaction, prefix: str):

    # 空白・改行だけ除去（大小文字は維持）
    prefix = prefix.strip()

    await interaction.response.defer()

    cache = await fetch_guild_data(prefix)

    if not cache:
        await interaction.edit_original_response(content="❌ ギルド取得に失敗しました")
        return

    g = cache["g"]
    online_by_rank = cache["onlineByRank"]
    online = cache["onlineCount"]
    total = cache["totalMembers"]

    # Owner
    owner_entry = next(iter(g["members"].get("owner", {}).items()), None)
    owner_name = owner_entry[0] if owner_entry else "Unknown"
    owner_server = owner_entry[1].get("server") if owner_entry else None
    owner_text = f"{owner_name} ({owner_server})" if owner_server else owner_name

    # Online text
    online_text = ""
    for rank, players in online_by_rank.items():
        if not players:
            continue

        online_text += f"**{rank.upper()}**\n"
        for p in players:
            wars = (p.get("wars", 0))
            wars_text = f"**{wars:,} wars**" if wars >= 1000 else f"{wars} wars"
            online_text += f"`{p['name']}` ({p['server']} | {wars_text})\n"
        online_text += "\n"

    if not online_text:
        online_text = "なし"

    embed = discord.Embed(
        title=f"{g['name']} [{g['prefix']}]",
        color=0x00BFFF
    )

    embed.add_field(name="<:crown:1467963602714624133> Owner", value=owner_text, inline=True)
    embed.add_field(name="<:poteti:1467555934199873680> Level", value=f"{g['level']} [{g['xpPercent']}%]", inline=True)
    embed.add_field(name="<:territory:1467963411999494305> Territories", value=str(g["territories"]), inline=True)
    embed.add_field(name="⚔️ Wars", value=str(g["wars"]), inline=True)
    embed.add_field(name=f"🟢 Online Members : {online}/{total}", value=online_text)

    embed.set_footer(text="Data from Wynncraft API")

    await interaction.edit_original_response(embed=embed)
