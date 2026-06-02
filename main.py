# =====================================
# main.py
# DEBUG VERSION
# =====================================

import os
import discord
from datetime import datetime

from discord.ext import commands, tasks

from history import load_history, save_history
from scanner import scan_market
from tracker import (
    save_signal,
    update_signals
)

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

last_top_report_hour = None

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
        name="DAY",
        value=f"{coin['day_change']:+.2f}%"
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
        name="DAY",
        value=f"{coin['day_change']:+.2f}%"
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


def build_top_longs_embed(longs):

    embed = discord.Embed(
        title="🔥 TOP LONGS RIGHT NOW",
        color=0x00ff00
    )

    for i, coin in enumerate(
        longs,
        start=1
    ):

        embed.add_field(
            name=f"#{i} {coin['symbol']}",
            value=(
                f"Score={coin['score']}\n"
                f"DAY={coin['day_change']:+.2f}%\n"
                f"OI1H={coin['oi_1h']:.2f}%\n"
                f"OI4H={coin['oi_4h']:.2f}%\n"
                f"VOL={coin['volume_change']:.2f}%"
            ),
            inline=False
        )

    return embed


def build_top_shorts_embed(shorts):

    embed = discord.Embed(
        title="🔻 TOP SHORTS RIGHT NOW",
        color=0xff0000
    )

    for i, coin in enumerate(
        shorts,
        start=1
    ):

        embed.add_field(
            name=f"#{i} {coin['symbol']}",
            value=(
                f"Score={coin['score']}\n"
                f"DAY={coin['day_change']:+.2f}%\n"
                f"OI1H={coin['oi_1h']:.2f}%\n"
                f"OI4H={coin['oi_4h']:.2f}%\n"
                f"VOL={coin['volume_change']:.2f}%"
            ),
            inline=False
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

        update_signals(
            history
        )

        global last_top_report_hour

        current_hour = (
            datetime.utcnow().hour
        )

        if (
            current_hour
            != last_top_report_hour
        ):

            await channel.send(
                embed=build_top_longs_embed(
                    longs
                )
            )

            await channel.send(
                embed=build_top_shorts_embed(
                    shorts
                )
            )

            last_top_report_hour = (
                current_hour
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

            save_signal(
                symbol=coin["symbol"],
                direction="LONG",
                score=coin["score"],
                day_change=coin["day_change"],
                entry_price=coin["price"]
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

            save_signal(
                symbol=coin["symbol"],
                direction="SHORT",
                score=coin["score"],
                day_change=coin["day_change"],
                entry_price=coin["price"]
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
