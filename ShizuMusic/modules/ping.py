# --------------------------------------------------------------------------------
#  ShizuMusic © 2026
#  Developed by Bad Munda ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import os
import time
from datetime import timedelta

import psutil
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ShizuMusic import bot, assistant, bot_start_time


def supp_markup():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🍬 sᴜᴘᴘᴏꝛᴛ 🍬",
                    url=config.SUPPORT_GROUP,
                ),
            ]
        ]
    )


@bot.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message) -> None:

    # Ping Start
    start = time.perf_counter()

    pm = await message.reply_text(
        f"<b>❍ {client.me.first_name} ɪs ᴘɪɴɢɪɴɢ...</b>",
        parse_mode=ParseMode.HTML,
    )

    latency = round((time.perf_counter() - start) * 1000)

    # Uptime
    uptime = str(
        timedelta(seconds=int(time.time() - bot_start_time))
    )

    # CPU Usage
    cpu = psutil.cpu_percent(interval=1)

    # BOT RAM Usage (real process usage)
    process = psutil.Process(os.getpid())

    ram = process.memory_info().rss / 1024 / 1024
    ram_str = f"{ram:.2f} MB"

    # Disk Usage
    disk = psutil.disk_usage("/")

    disk_str = (
        f"{disk.used // (1024**3)}GB / "
        f"{disk.total // (1024**3)}GB "
        f"({disk.percent}%)"
    )

    # Assistant Ping
    try:
        pytg_start = time.perf_counter()

        await assistant.get_me()

        pytg = round(
            (time.perf_counter() - pytg_start) * 1000
        )

    except Exception:
        pytg = "N/A"

    # Delete the "pinging..." message
    await pm.delete()

    # Caption text
    caption = f"""
<b>🏓 ᴘᴏɴɢ : <code>{latency}ms</code></b>

<b><u>{client.me.first_name} sʏsᴛᴇᴍ sᴛᴀᴛs :</u></b>

<b>❍ ᴜᴘᴛɪᴍᴇ :</b> <code>{uptime}</code>
<b>❍ ʀᴀᴍ :</b> <code>{ram_str}</code>
<b>❍ ᴄᴘᴜ :</b> <code>{cpu}%</code>
<b>❍ ᴅɪsᴋ :</b> <code>{disk_str}</code>
<b>❍ ᴘʏᴛɢᴄ :</b> <code>{pytg}ms</code>

<b>❍ 𝖡ʏ » <a href="{config.SUPPORT_GROUP}">sʜɪᴢᴜ-ᴍᴜsɪᴄ™</a></b>
"""

    # Send photo with caption + support button
    await message.reply_photo(
        photo=config.PING_IMG_URL,
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=supp_markup(),
    )
