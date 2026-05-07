"""
ShizuMusic/modules/ping.py
/ping command — latency, uptime, and system stats.
"""

import os
import time
from datetime import timedelta

import psutil
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ShizuMusic import bot, bot_start_time, call_py


@bot.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message):
    start = time.perf_counter()

    msg = await message.reply_text(
        f"<b>❍ {client.me.first_name} ɪs ᴘɪɴɢɪɴɢ...</b>",
        parse_mode=ParseMode.HTML,
    )

    latency = round((time.perf_counter() - start) * 1000)

    # Uptime
    uptime = str(
        timedelta(seconds=int(time.time() - bot_start_time))
    )

    # Bot process stats
    process = psutil.Process(os.getpid())

    ram_usage = round(process.memory_info().rss / 1024 / 1024, 2)

    cpu_usage = psutil.cpu_percent(interval=1)

    disk = psutil.disk_usage("/")
    disk_usage = (
        f"{disk.used // (1024**3)}GB / "
        f"{disk.total // (1024**3)}GB "
        f"({disk.percent}%)"
    )

    # PyTgCalls Ping
    pytgcalls_ping = "N/A"

    try:
        ping_start = time.perf_counter()

        # lightweight call
        await call_py.get_me()

        pytgcalls_ping = round(
            (time.perf_counter() - ping_start) * 1000
        )

    except Exception:
        pass

    await msg.edit_text(
        f"""
<b>🏓 ᴘᴏɴɢ : <code>{latency} ms</code></b>

<b><u>{client.me.first_name} sʏsᴛᴇᴍ sᴛᴀᴛs :</u></b>

<b>❍ ᴜᴘᴛɪᴍᴇ :</b> <code>{uptime}</code>
<b>❍ ʀᴀᴍ :</b> <code>{ram_usage} MB</code>
<b>❍ ᴄᴘᴜ :</b> <code>{cpu_usage}%</code>
<b>❍ ᴅɪsᴋ :</b> <code>{disk_usage}</code>
<b>❍ ᴘʏᴛɢᴄ :</b> <code>{pytgcalls_ping} ms</code>

<b>❍ 𝖡ʏ » <a href="{config.SUPPORT_GROUP}">sʜɪᴢᴜ-ᴍᴜsɪᴄ™</a></b>
""",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
