"""
ShizuMusic/modules/stop.py
/stop and /end commands — stop playback and clear queue (admin only).
/clear command — clear queue without stopping (admin only).
/reboot command — reset all chat state.
"""
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ShizuMusic import bot, call_py
from ShizuMusic.core.call import leave_vc
from ShizuMusic.core.queue import clear_queue, queue_size
from ShizuMusic.utils.permissions import is_user_authorized


@bot.on_message(filters.group & filters.command(["stop", "end"]))
async def stop_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply("<b>❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.</b>", parse_mode=ParseMode.HTML)
        return
    chat_id = message.chat.id
    await leave_vc(chat_id)
    await message.reply(
        "<b>⏹ sᴛᴏᴩᴩᴇᴅ & ǫᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ.</b>",
        parse_mode=ParseMode.HTML,
    )


@bot.on_message(filters.group & filters.command("clear"))
async def clear_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply("<b>❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.</b>", parse_mode=ParseMode.HTML)
        return
    chat_id = message.chat.id
    if not queue_size(chat_id):
        await message.reply("<b>❌ ǫᴜᴇᴜᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴇᴍᴘᴛʏ.</b>", parse_mode=ParseMode.HTML)
        return
    clear_queue(chat_id)
    await message.reply("<b>🗑️ ǫᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ.</b>", parse_mode=ParseMode.HTML)


@bot.on_message(filters.command("reboot"))
async def reboot_cmd(_, message: Message) -> None:
    chat_id = message.chat.id
    await leave_vc(chat_id)
    await message.reply("<b>♻️ ᴄʜᴀᴛ sᴛᴀᴛᴇ ʀᴇsᴇᴛ.</b>", parse_mode=ParseMode.HTML)
