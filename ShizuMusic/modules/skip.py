"""
ShizuMusic/modules/skip.py

/skip command — skip current song and play next.
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


# ─────────────────────────────────────────────
# SKIP SONG
# ─────────────────────────────────────────────
@bot.on_message(filters.group & filters.command("skip"))
async def skip_cmd(_, message: Message) -> None:

    chat_id = message.chat.id

    # Admin Check
    if not await is_user_authorized(message):

        await message.reply(
            """
<b>❍ ᴀᴅᴍɪɴ ᴏɴʟʏ</b>
<b>❍ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ғᴏʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs.</b>
""",
            parse_mode=ParseMode.HTML,
        )
        return

    # Queue Check
    if not queue_size(chat_id):

        await message.reply(
            """
<b>❍ ǫᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ</b>
<b>❍ ɴᴏ sᴏɴɢs ᴛᴏ sᴋɪᴘ.</b>
""",
            parse_mode=ParseMode.HTML,
        )
        return

    # Skipping Message
    sm = await message.reply(
        """
<b>❍ sᴋɪᴘᴘɪɴɢ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ...</b>
""",
        parse_mode=ParseMode.HTML,
    )

    # Remove Current Song
    skipped = pop_current(chat_id)

    # Leave Current Stream
    try:
        await call_py.leave_call(chat_id)

    except Exception:
        pass

    # Cleanup
    await asyncio.sleep(2)

    try:
        delete_file(skipped.get("file_path", ""))

    except Exception:
        pass

    # Next Song
    nxt = peek_current(chat_id)

    if nxt:

        await sm.edit_text(
            f"""
<b>❍ sᴋɪᴘᴘᴇᴅ ᴛʀᴀᴄᴋ :</b><code>{short(skipped['title'])}</code>
<b>❍ ɴᴏᴡ ᴘʟᴀʏɪɴɢ :</b>
<code>{nxt['title']}</code>
""",
            parse_mode=ParseMode.HTML,
        )

        dm = await bot.send_message(
            chat_id,
            f"""
<b>❍ ɴᴇxᴛ ᴛʀᴀᴄᴋ :</b><code>{nxt['title']}</code>
""",
            parse_mode=ParseMode.HTML,
        )

        await play_song(chat_id, dm, nxt)

    else:

        await sm.edit_text(
            f"""
<b>❍ sᴋɪᴘᴘᴇᴅ ᴛʀᴀᴄᴋ :</b><code>{short(skipped['title'])}</code>
<b>❍ ǫᴜᴇᴜᴇ ɪs ɴᴏᴡ ᴇᴍᴘᴛʏ</b>
""",
            parse_mode=ParseMode.HTML,
        )
