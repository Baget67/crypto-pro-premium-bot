# =====================================
# main.py
# Crypto Pro Premium Bot V2
# =====================================

import os
import discord

from discord.ext import (
    commands,
    tasks
)

from history import (
    load_history,
    save_history
)

from scanner import (
    scan_market
)

from config import (
    SCAN_INTERVAL_MINUTES,
    LONG_ALERT_SCORE,
    SHORT_ALERT_SCORE
)

# =====================================
# ENV
# =====================================

BOT_TOKEN = os.getenv(
    "DISCORD_BOT_TOKEN"
)

CHANNEL_ID = int(
    os.getenv(
        "DISCORD_CHANNEL_ID",
        "0"
    )
)

# =====================================
# DISCORD
# =====================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

history = load_history()

# cooldown cache

last_alerts = {}


# =====================================
# EMBEDS
# =====================================

def build_long_embed(
    coin
):
    embed = discord.Embed(
        title=f"🚀 LONG ALERT - {coin['symbol']}",
        color=0x00ff00
    )

    embed.add_field(
        name="Score",
        value=str(
            coin["score"]
        )
    )

    embed.add_field(
        name="OI 1H",
        value=f"{coin['oi_1h']:.2f}%"
    )

    embed.add_field(
        name="OI 4H",
        value=f"{coin['oi_4h']:.2f}%"
    )

    embed.add_field(
        name="Volume",
        value=f"{coin['volume_change']:.2f}%"
    )

    embed.add_field(
        name="Funding",
        value=f"{coin['funding']:.5f}"
    )

    embed.add_field(
        name="Reasons",
        value="\n".join(
            coin["reasons"]
        )[:1000],
        inline=False
    )

    return embed


def build_short_embed(
    coin
):
    embed = discord.Embed(
        title=f"🔻 SHORT ALERT - {coin['symbol']}",
        color=0xff0000
    )

    embed.add_field(
        name="Score",
        value=str(
            coin["score"]
        )
    )

    embed.add_field(
        name="OI 1H",
        value=f"{coin['oi_1h']:.2f}%"
    )

    embed.add_field(
        name="OI 4H",
        value=f"{coin['oi_4h']:.2f}%"
    )

    embed.add_field(
        name="Volume",
        value=f"{coin['volume_change']:.2f}%"
    )

    embed.add_field(
        name="Funding",
        value=f"{coin['funding']:.5f}"
    )

    embed.add_field(
        name="Reasons",
        value="\n".join(
            coin["reasons"]
        )[:1000],
        inline=False
    )

    return embed


# =====================================
# COMMANDS
# =====================================

@bot.command()
async def scan(ctx):

    longs, shorts = await scan_market(
        history
    )

    await ctx.send(
        f"Found {len(longs)} longs "
        f"and {len(shorts)} shorts"
    )


@bot.command()
async def top(ctx):

    longs, shorts = await scan_market(
        history
    )

    for coin in longs:
        await ctx.send(
            embed=build_long_embed(
                coin
            )
        )

    for coin in shorts:
        await ctx.send(
            embed=build_short_embed(
                coin
            )
        )


# =====================================
# AUTO LOOP
# =====================================

@tasks.loop(
    minutes=SCAN_INTERVAL_MINUTES
)
async def market_loop():

    channel = bot.get_channel(
        CHANNEL_ID
    )

    if channel is None:
        return

    longs, shorts = await scan_market(
        history
    )

    for coin in longs:

        if (
            coin["score"]
            >= LONG_ALERT_SCORE
        ):
            await channel.send(
                embed=build_long_embed(
                    coin
                )
            )

    for coin in shorts:

        if (
            coin["score"]
            >= SHORT_ALERT_SCORE
        ):
            await channel.send(
                embed=build_short_embed(
                    coin
                )
            )

    save_history(
        history
    )


# =====================================
# READY
# =====================================

@bot.event
async def on_ready():

    print(
        f"Logged in as "
        f"{bot.user}"
    )

    if not market_loop.is_running():
        market_loop.start()


# =====================================
# START
# =====================================

bot.run(
    BOT_TOKEN
)