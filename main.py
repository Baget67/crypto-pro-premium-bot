# =====================================
# main.py
# DEBUG VERSION
# =====================================

import os
import discord

from discord.ext import commands, tasks

from history import load_history, save_history
from scanner import scan_market

from config import (
    SCAN_INTERVAL_MINUTES,
    LONG_ALERT_SCORE,
    SHORT_ALERT_SCORE
)

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

CHANNEL_ID = int(
    os.getenv(
        "DISCORD_CHANNEL_ID",
        "0"
    )
)

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

history = load_history()


def build_long_embed(coin):

    embed = discord.Embed(
        title=f"🚀 LONG ALERT - {coin['symbol']}",
        color=0x00ff00
    )

    embed.add_field(
        name="Score",
        value=str(coin["score"])
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

    return embed


def build_short_embed(coin):

    embed = discord.Embed(
        title=f"🔻 SHORT ALERT - {coin['symbol']}",
        color=0xff0000
    )

    embed.add_field(
        name="Score",
        value=str(coin["score"])
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

    return embed


@tasks.loop(
    minutes=SCAN_INTERVAL_MINUTES
)
async def market_loop():

    print("=" * 50)
    print("MARKET LOOP STARTED")
    print("=" * 50)

    try:

        channel = bot.get_channel(
            CHANNEL_ID
        )

        if channel is None:

            print(
                f"ERROR: Channel not found: {CHANNEL_ID}"
            )

            return

        print(
            f"Channel found: {channel.name}"
        )

        longs, shorts = await scan_market(
            history
        )

        print(
            f"Longs found: {len(longs)}"
        )

        print(
            f"Shorts found: {len(shorts)}"
        )

        for coin in longs:

            print(
                f"LONG {coin['symbol']} "
                f"score={coin['score']}"
            )

            if coin["score"] >= LONG_ALERT_SCORE:

                await channel.send(
                    embed=build_long_embed(
                        coin
                    )
                )

                print(
                    f"SENT LONG: "
                    f"{coin['symbol']}"
                )

        for coin in shorts:

            print(
                f"SHORT {coin['symbol']} "
                f"score={coin['score']}"
            )

            if coin["score"] >= SHORT_ALERT_SCORE:

                await channel.send(
                    embed=build_short_embed(
                        coin
                    )
                )

                print(
                    f"SENT SHORT: "
                    f"{coin['symbol']}"
                )

        save_history(
            history
        )

        print(
            "History saved"
        )

    except Exception as e:

        print(
            f"MARKET LOOP ERROR: {e}"
        )


@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}"
    )

    print(
        "Starting market loop..."
    )

    if not market_loop.is_running():

        market_loop.start()

        print(
            "Market loop started"
        )


bot.run(
    BOT_TOKEN
)
