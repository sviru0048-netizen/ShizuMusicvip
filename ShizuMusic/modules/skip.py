"""
ShizuMusic/modules/skip.py
/skip command — skip current song and play next (admin only).
"""
import asyncio

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ShizuMusic import bot, call_py
from ShizuMusic.core.player import play_song
from ShizuMusic.core.queue import peek_current, pop_current, queue_size
from ShizuMusic.utils.formatters import short
from ShizuMusic.utils.helpers import delete_file
from ShizuMusic.utils.permissions import is_user_authorized


@bot.on_message(filters.group & filters.command("skip"))
async def skip_cmd(_, message: Message) -> None:
    chat_id = message.chat.id

    if not await is_user_authorized(message):
        await message.reply("<b>❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.</b>", parse_mode=ParseMode.HTML)
        return

    if not queue_size(chat_id):
        await message.reply("<b>❌ ǫᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ.</b>", parse_mode=ParseMode.HTML)
        return

    sm = await message.reply("<b>⏭ sᴋɪᴩᴩɪɴɢ…</b>", parse_mode=ParseMode.HTML)
    skipped = pop_current(chat_id)

    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass

    await asyncio.sleep(2)
    delete_file(skipped.get("file_path", ""))

    nxt = peek_current(chat_id)
    if nxt:
        await sm.edit(
            f"<b>⏭ sᴋɪᴩᴩᴇᴅ :</b> {short(skipped['title'])}\n"
            f"<b>▶️ ɴᴇxᴛ   :</b> {nxt['title']}",
            parse_mode=ParseMode.HTML,
        )
        dm = await bot.send_message(
            chat_id,
            f"<b>🎧 ɴᴇxᴛ :</b> {nxt['title']}",
            parse_mode=ParseMode.HTML,
        )
        await play_song(chat_id, dm, nxt)
    else:
        await sm.edit(
            f"<b>⏭ sᴋɪᴩᴩᴇᴅ :</b> {short(skipped['title'])}. <b>ǫᴜᴇᴜᴇ ᴇᴍᴘᴛʏ.</b>",
            parse_mode=ParseMode.HTML,
        )
