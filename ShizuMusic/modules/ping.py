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
from ShizuMusic import bot, assistant, bot_start_time


@bot.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message) -> None:

    # ── Ping Start ────────────────────────────
    start = time.perf_counter()

    pm = await message.reply_photo(
        photo=config.PING_IMG_URL,
        caption=f"<b>❍ {client.me.first_name} ɪs ᴘɪɴɢɪɴɢ...</b>",
        parse_mode=ParseMode.HTML,
    )

    latency = round((time.perf_counter() - start) * 1000)

    # ── Uptime ────────────────────────────────
    uptime = str(
        timedelta(seconds=int(time.time() - bot_start_time))
    )

    # ── CPU ───────────────────────────────────
    cpu = psutil.cpu_percent(interval=1)

    # ── RAM ───────────────────────────────────
    process = psutil.Process(os.getpid())
    ram = process.memory_info().rss / 1024 / 1024
    ram_str = f"{ram:.2f} MB"

    # ── Disk ──────────────────────────────────
    disk = psutil.disk_usage("/")
    disk_str = (
        f"{disk.used // (1024**3)}GB / "
        f"{disk.total // (1024**3)}GB "
        f"({disk.percent}%)"
    )

    # ── Assistant Ping ────────────────────────
    try:
        pytg_start = time.perf_counter()
        await assistant.get_me()
        pytg = f"{round((time.perf_counter() - pytg_start) * 1000)}ms"
    except Exception:
        pytg = "N/A"

    # ── Final Caption ─────────────────────────
    caption = (
        f"<b>🏓 ᴘᴏɴɢ : <code>{latency}ms</code></b>\n\n"
        f"<b><u>{client.me.first_name} sʏsᴛᴇᴍ sᴛᴀᴛs :</u></b>\n\n"
        f"<b>❍ ᴜᴘᴛɪᴍᴇ :</b> <code>{uptime}</code>\n"
        f"<b>❍ ʀᴀᴍ :</b> <code>{ram_str}</code>\n"
        f"<b>❍ ᴄᴘᴜ :</b> <code>{cpu}%</code>\n"
        f"<b>❍ ᴅɪsᴋ :</b> <code>{disk_str}</code>\n"
        f"<b>❍ ᴘʏᴛɢᴄ :</b> <code>{pytg}</code>\n\n"
        f"<b>❍ 𝖡ʏ » <a href=\"{config.SUPPORT_GROUP}\">sʜɪᴢᴜ-ᴍᴜsɪᴄ™</a></b>"
    )

    await pm.edit_caption(
        caption=caption,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
