"""
ShizuMusic/modules/moderation.py
Group moderation commands — mute, unmute, kick, ban, unban (admin only).
"""
import asyncio

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import ChatPermissions, Message

from ShizuMusic import bot
from ShizuMusic.utils.permissions import is_user_authorized


async def _get_target(message: Message) -> int | None:
    """Resolve target user from reply or @username argument."""
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴩʀᴏᴠɪᴅᴇ @ᴜsᴇʀɴᴀᴍᴇ")
        return None
    try:
        u = await bot.get_users(parts[1].lstrip("@"))
        return u.id
    except Exception:
        await message.reply("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ")
        return None


@bot.on_message(filters.group & filters.command("mute"))
async def mute_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply("<b>❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.</b>", parse_mode=ParseMode.HTML)
        return
    uid = await _get_target(message)
    if not uid:
        return
    try:
        await bot.restrict_chat_member(message.chat.id, uid, ChatPermissions())
        await message.reply("<b>🔇 ᴜsᴇʀ ᴍᴜᴛᴇᴅ.</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌</b> <code>{e}</code>", parse_mode=ParseMode.HTML)


@bot.on_message(filters.group & filters.command("unmute"))
async def unmute_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply("<b>❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.</b>", parse_mode=ParseMode.HTML)
        return
    uid = await _get_target(message)
    if not uid:
        return
    try:
        await bot.restrict_chat_member(
            message.chat.id,
            uid,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_invite_users=True,
            ),
        )
        await message.reply("<b>🔊 ᴜsᴇʀ ᴜɴᴍᴜᴛᴇᴅ.</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌</b> <code>{e}</code>", parse_mode=ParseMode.HTML)


@bot.on_message(filters.group & filters.command("kick"))
async def kick_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply("<b>❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.</b>", parse_mode=ParseMode.HTML)
        return
    uid = await _get_target(message)
    if not uid:
        return
    try:
        await bot.ban_chat_member(message.chat.id, uid)
        await asyncio.sleep(1)
        await bot.unban_chat_member(message.chat.id, uid)
        await message.reply("<b>👢 ᴜsᴇʀ ᴋɪᴄᴋᴇᴅ.</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌</b> <code>{e}</code>", parse_mode=ParseMode.HTML)


@bot.on_message(filters.group & filters.command("ban"))
async def ban_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply("<b>❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.</b>", parse_mode=ParseMode.HTML)
        return
    uid = await _get_target(message)
    if not uid:
        return
    try:
        await bot.ban_chat_member(message.chat.id, uid)
        await message.reply("<b>🔨 ᴜsᴇʀ ʙᴀɴɴᴇᴅ.</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌</b> <code>{e}</code>", parse_mode=ParseMode.HTML)


@bot.on_message(filters.group & filters.command("unban"))
async def unban_cmd(_, message: Message) -> None:
    if not await is_user_authorized(message):
        await message.reply("<b>❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.</b>", parse_mode=ParseMode.HTML)
        return
    uid = await _get_target(message)
    if not uid:
        return
    try:
        await bot.unban_chat_member(message.chat.id, uid)
        await message.reply("<b>✅ ᴜsᴇʀ ᴜɴʙᴀɴɴᴇᴅ.</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌</b> <code>{e}</code>", parse_mode=ParseMode.HTML)
