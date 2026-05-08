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

from ShizuMusic import bot
from ShizuMusic.core.call import leave_vc
from ShizuMusic.core.queue import clear_queue, queue_size
from ShizuMusic.utils.permissions import is_user_authorized


# ─────────────────────────────────────────────
# STOP / END
# ─────────────────────────────────────────────
@bot.on_message(filters.group & filters.command(["stop", "end"]))
async def stop_cmd(_, message: Message) -> None:

    if not await is_user_authorized(message):

        await message.reply(
            """
<b>❍ ᴀᴅᴍɪɴ ᴏɴʟʏ</b>
<b>❍ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ғᴏʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs.</b>
""",
            parse_mode=ParseMode.HTML,
        )
        return

    chat_id = message.chat.id

    await leave_vc(chat_id)

    await message.reply(
        """
<b>❍ ᴘʟᴀʏʙᴀᴄᴋ sᴛᴏᴘᴘᴇᴅ</b>
<b>❍ ǫᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ</b>
<b>❍ ʟᴇғᴛ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ</b>
""",
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────
# CLEAR QUEUE
# ─────────────────────────────────────────────
@bot.on_message(filters.group & filters.command("clear"))
async def clear_cmd(_, message: Message) -> None:

    if not await is_user_authorized(message):

        await message.reply(
            """
<b>❍ ᴀᴅᴍɪɴ ᴏɴʟʏ</b>
<b>❍ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ғᴏʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs.</b>
""",
            parse_mode=ParseMode.HTML,
        )
        return

    chat_id = message.chat.id

    if not queue_size(chat_id):

        await message.reply(
            """
<b>❍ ǫᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ</b>
<b>❍ ɴᴏ sᴏɴɢs ɪɴ ǫᴜᴇᴜᴇ.</b>
""",
            parse_mode=ParseMode.HTML,
        )
        return

    clear_queue(chat_id)

    await message.reply(
        """
<b>❍ ǫᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ</b>
<b>❍ ᴀʟʟ ᴘᴇɴᴅɪɴɢ sᴏɴɢs ʀᴇᴍᴏᴠᴇᴅ.</b>
""",
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────
# REBOOT CHAT STATE
# ─────────────────────────────────────────────
@bot.on_message(filters.command("reboot"))
async def reboot_cmd(_, message: Message) -> None:

    chat_id = message.chat.id

    await leave_vc(chat_id)

    await message.reply(
        """
<b>❍ ᴄʜᴀᴛ ʀᴇʙᴏᴏᴛᴇᴅ</b>
<b>❍ ᴀʟʟ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ sᴛᴀᴛᴇs ʀᴇsᴇᴛ.</b>
""",
        parse_mode=ParseMode.HTML,
    )
