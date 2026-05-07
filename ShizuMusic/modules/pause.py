"""
ShizuMusic/modules/pause.py

/pause command — pause current stream.
"""

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ShizuMusic import bot, call_py
from ShizuMusic.utils.permissions import is_user_authorized


# ─────────────────────────────────────────────
# PAUSE STREAM
# ─────────────────────────────────────────────
@bot.on_message(filters.group & filters.command("pause"))
async def pause_cmd(_, message: Message) -> None:

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

    # Pause Stream
    try:

        await call_py.pause(message.chat.id)

        await message.reply(
            """
<b>❍ sᴛʀᴇᴀᴍ ᴘᴀᴜsᴇᴅ</b>
<b>❍ ᴍᴜsɪᴄ ᴘʟᴀʏʙᴀᴄᴋ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ sᴛᴏᴘᴘᴇᴅ.</b>
""",
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:

        await message.reply(
            f"""
<b>❍ ᴘᴀᴜsᴇ ғᴀɪʟᴇᴅ</b><code>{e}</code>
""",
            parse_mode=ParseMode.HTML,
        )
