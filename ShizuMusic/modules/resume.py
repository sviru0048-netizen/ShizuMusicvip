# --------------------------------------------------------------------------------
#  ShizuMusic © 2026
#  Developed by Bad Munda ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ShizuMusic import bot, call_py
from ShizuMusic.utils.permissions import is_user_authorized


# ─────────────────────────────────────────────
# RESUME STREAM
# ─────────────────────────────────────────────
@bot.on_message(filters.group & filters.command("resume"))
async def resume_cmd(_, message: Message) -> None:

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

    # Resume Stream
    try:

        await call_py.resume(message.chat.id)

        await message.reply(
            """
<b>❍ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ</b>
<b>❍ ᴍᴜsɪᴄ ᴘʟᴀʏʙᴀᴄᴋ ᴄᴏɴᴛɪɴᴜᴇᴅ.</b>
""",
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:

        await message.reply(
            f"""
<b>❍ ʀᴇsᴜᴍᴇ ғᴀɪʟᴇᴅ</b>
<code>{e}</code>
""",
            parse_mode=ParseMode.HTML,
        )
