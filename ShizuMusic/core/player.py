"""
ShizuMusic/core/player.py
Core music player — resolve, stream, progress UI.
"""
import asyncio
import time

from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls.types import MediaStream

import config
from ShizuMusic import LOGGER, bot, call_py
from ShizuMusic.utils.formatters import fmt_time, progress_bar, short
from ShizuMusic.utils.youtube import resolve_stream


async def _update_progress(
    chat_id: int,
    msg: Message,
    start_t: float,
    total: float,
    caption: str,
) -> None:
    """Edit playback message every 18 s with live progress bar."""
    btns = [
        InlineKeyboardButton("▷", callback_data="resume"),
        InlineKeyboardButton("II",  callback_data="pause"),
        InlineKeyboardButton("‣‣I",  callback_data="skip"),
        InlineKeyboardButton("▢",  callback_data="stop"),
    ]
    while True:
        elapsed = min(time.time() - start_t, total)
        bar = progress_bar(elapsed, total)
        kb  = InlineKeyboardMarkup([btns, [InlineKeyboardButton(bar, callback_data="noop")]])
        try:
            await bot.edit_message_caption(chat_id, msg.id, caption=caption, reply_markup=kb)
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" not in str(e):
                break
        if elapsed >= total:
            break
        await asyncio.sleep(18)


async def play_song(chat_id: int, message: Message, song: dict) -> None:
    """Download (if needed) and stream a song into the voice chat."""
    url = song.get("url")
    if not url:
        return

    # Loading indicator
    loading_text = (
        "<b>╭────────────────────▣</b>\n"
        f"<b>│❍ ʟᴏᴀᴅɪɴɢ :</b> {short(song['title'])}\n"
        "<b>│❍ sᴇʀᴠᴇʀ ᴡᴀʀᴍɪɴɢ ᴜᴩ…</b>\n"
        "<b>╰────────────────────▣</b>"
    )
    try:
        await message.edit(loading_text, parse_mode=ParseMode.HTML)
    except Exception:
        message = await bot.send_message(chat_id, loading_text, parse_mode=ParseMode.HTML)

    # Resolve audio path
    try:
        media_path = await resolve_stream(url)
    except Exception as e:
        await bot.send_message(
            chat_id,
            f"<b>❌ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ</b>\n\n<code>{e}</code>\n\n"
            "<i>ᴩʟᴇᴀsᴇ ᴛʀʏ /play ᴀɢᴀɪɴ</i>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Start PyTgCalls
    try:
        await call_py.play(chat_id, MediaStream(media_path, video_flags=MediaStream.Flags.IGNORE))
    except Exception as e:
        await bot.send_message(
            chat_id,
            f"<b>❌ ᴘʟᴀʏʙᴀᴄᴋ ғᴀɪʟᴇᴅ :</b> <code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Build now-playing UI
    from ShizuMusic.utils.formatters import parse_dur
    total   = parse_dur(song.get("duration", "0:00"))
    caption = (
        "<blockquote>"
        "<b>🎧 Sʜɪᴢᴜ Mᴜsɪᴄ</b>\n\n"
        f"<b>❍ ᴛɪᴛʟᴇ :</b> {short(song['title'])}\n"
        f"<b>❍ ᴅᴜʀ   :</b> {song.get('duration', '?')}\n"
        f"<b>❍ ʙʏ    :</b> {song['requester']}"
        "</blockquote>"
    )
    btns = [
        InlineKeyboardButton("▷", callback_data="resume"),
        InlineKeyboardButton("II",  callback_data="pause"),
        InlineKeyboardButton("‣‣I",  callback_data="skip"),
        InlineKeyboardButton("▢",  callback_data="stop"),
    ]
    bar = progress_bar(0, total)
    kb  = InlineKeyboardMarkup([btns, [InlineKeyboardButton(bar, callback_data="noop")]])

    thumb = song.get("thumbnail")
    try:
        pmsg = await message.reply_photo(
            photo=thumb, caption=caption, reply_markup=kb, parse_mode=ParseMode.HTML
        )
    except Exception:
        pmsg = await bot.send_message(chat_id, caption, reply_markup=kb, parse_mode=ParseMode.HTML)

    try:
        await message.delete()
    except Exception:
        pass

    # Progress updater + logger
    asyncio.create_task(_update_progress(chat_id, pmsg, time.time(), total, caption))

    if config.LOGGER_ID:
        asyncio.create_task(bot.send_message(
            config.LOGGER_ID,
            "<b>#ɴᴏᴡᴘʟᴀʏɪɴɢ</b>\n"
            f"• <b>ᴛɪᴛʟᴇ :</b> {song.get('title')}\n"
            f"• <b>ᴅᴜʀ   :</b> {song.get('duration')}\n"
            f"• <b>ʙʏ    :</b> {song.get('requester')}",
            parse_mode=ParseMode.HTML,
        ))
