"""
ShizuMusic/modules/ping.py
/ping command — latency, uptime, and system stats.
"""
import time
from datetime import timedelta

import psutil
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ShizuMusic import bot, bot_start_time, call_py


@bot.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message) -> None:
    start   = time.time()
    pm      = await message.reply_text(
        f"<b>❍ {client.me.first_name} ɪs ᴘɪɴɢɪɴɢ…</b>",
        parse_mode=ParseMode.HTML,
    )
    latency = round((time.time() - start) * 1000)
    uptime  = str(timedelta(seconds=int(time.time() - bot_start_time)))

    cpu  = psutil.cpu_percent(interval=0.5)
    mem  = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    ram_str  = f"{mem.used // 1048576}MB / {mem.total // 1048576}MB ({mem.percent}%)"
    disk_str = f"{disk.used // 1073741824}GB / {disk.total // 1073741824}GB ({disk.percent}%)"

    try:
        ps = time.time()
        await call_py.ping()
        pytg = round((time.time() - ps) * 1000)
    except Exception:
        pytg = "N/A"

    await pm.edit(
        f"<b>🏓 ᴩᴏɴɢ : <code>{latency}ms</code></b>\n\n"
        f"<b><u>{client.me.first_name} sʏsᴛᴇᴍ sᴛᴀᴛs :</u></b>\n\n"
        f"<b>❍ ᴜᴩᴛɪᴍᴇ :</b> {uptime}\n"
        f"<b>❍ ʀᴀᴍ    :</b> {ram_str}\n"
        f"<b>❍ ᴄᴩᴜ    :</b> {cpu}%\n"
        f"<b>❍ ᴅɪsᴋ   :</b> {disk_str}\n"
        f"<b>❍ ᴩʏᴛɢᴄ  :</b> <code>{pytg}ms</code>\n\n"
        f"<b>❍ 𝖡ʏ » <a href='{config.SUPPORT_GROUP}'>sʜɪᴢᴜ-ᴍᴜ𝛅𝛊ᴄ™</a></b>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
