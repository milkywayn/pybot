import time
import asyncio
import aiohttp

GUILD_CACHE = {}
WAR_CACHE = {}

CACHE_TIME = 60
WAR_CACHE_TIME = 60

HEADERS = {"User-Agent": "DiscordBot/1.0"}


async def fetch_player_wars(player: str) -> int:
    now = time.time()

    if player in WAR_CACHE and now - WAR_CACHE[player]["time"] < WAR_CACHE_TIME:
        return WAR_CACHE[player]["wars"]

    url = f"https://api.wynncraft.com/v3/player/{player}"

    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url) as res:
                if res.status != 200:
                    return 0
                data = await res.json()

        wars = data.get("globalData", {}).get("wars", 0)

        WAR_CACHE[player] = {"wars": wars, "time": now}
        return wars

    except Exception as e:
        print("fetch_guild_data error:", e)
    return None



async def fetch_guild_data(prefix: str):
    now = time.time()

    if prefix in GUILD_CACHE and now - GUILD_CACHE[prefix]["time"] < CACHE_TIME:
        return GUILD_CACHE[prefix]["data"]

    url = f"https://api.wynncraft.com/v3/guild/prefix/{prefix}"

    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url) as res:
                if res.status != 200:
                    return None
                g = await res.json()

        if "members" not in g:
            return None

        online_by_rank = {
            "owner": [],
            "chief": [],
            "strategist": [],
            "captain": [],
            "recruiter": [],
            "recruit": []
        }

        total = 0
        online = 0

        for rank, members in g["members"].items():
            for name, data in members.items():
                total += 1
                if data.get("online"):
                    online += 1
                    online_by_rank[rank].append({
                        "name": name,
                        "server": data.get("server", "?")
                    })

        # 最大15人まで
        online_list = [p for r in online_by_rank.values() for p in r][:15]

        wars_list = await asyncio.gather(
            *(fetch_player_wars(p["name"]) for p in online_list)
        )

        i = 0
        for rank in online_by_rank:
            for p in online_by_rank[rank]:
                if i < len(wars_list):
                    p["wars"] = wars_list[i]
                    i += 1
                else:
                    p["wars"] = 0

        data = {
            "g": g,
            "onlineByRank": online_by_rank,
            "onlineCount": online,
            "totalMembers": total
        }

        GUILD_CACHE[prefix] = {"data": data, "time": now}
        return data

    except Exception as e:
        print("fetch_guild_data error:", e)
    return None

