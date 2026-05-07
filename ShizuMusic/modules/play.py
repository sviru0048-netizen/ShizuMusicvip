"""
ShizuMusic/modules/play.py
/play command — single track, playlist, and replied audio/video.
"""
import asyncio
import re
import time

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import RPCError, UserAlreadyParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ShizuMusic import bot
from ShizuMusic.core.player import play_song
from ShizuMusic.core.queue import add_to_queue, queue_size
from ShizuMusic.utils.formatters import fmt_time, iso_to_human, iso_to_sec, short
from ShizuMusic.utils.youtube import search_yt

# ── State ─────────────────────────────────────────────────────────────────────
_last_cmd: dict[int, float] = {}
_pending:  dict[int, tuple] = {}


# ── Assistant helpers ─────────────────────────────────────────────────────────

async def _get_invite(chat_id: int) -> str | None:
    try:
        chat = await bot.get_chat(chat_id)
        return chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else None)
    except Exception:
        return None


async def _is_assistant_in(chat_id: int, assistant_username: str):
    from ShizuMusic import assistant
    try:
        m = await assistant.get_chat_member(chat_id, assistant_username)
        return m.status is not None
    except Exception as e:
        s = str(e)
        if "USER_BANNED" in s or "Banned" in s:
            return "banned"
        return False


async def _invite_assistant(chat_id: int, link: str, msg: Message) -> bool:
    from ShizuMusic import assistant
    try:
        await assistant.join_chat(link)
        return True
    except UserAlreadyParticipant:
        return True
    except RPCError as e:
        await msg.edit(f"❌ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴ ғᴀɪʟᴇᴅ: {e.error_message}")
        return False
    except Exception as e:
        await msg.edit(f"❌ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴ ғᴀɪʟᴇᴅ: {e}")
        return False


# ── Cooldown runner ───────────────────────────────────────────────────────────

async def _run_pending(chat_id: int, delay: int) -> None:
    await asyncio.sleep(delay)
    if chat_id in _pending:
        msg, reply = _pending.pop(chat_id)
        try:
            await reply.delete()
        except Exception:
            pass
        await play_handler(bot, msg)


# ── /play handler ─────────────────────────────────────────────────────────────

@bot.on_message(filters.group & filters.regex(r'^/play(?:@\w+)?(?:\s+(?P<q>.+))?$'))
async def play_handler(_, message: Message) -> None:
    chat_id = message.chat.id

    # Replied audio/video
    if message.reply_to_message and (
        message.reply_to_message.audio or message.reply_to_message.video
    ):
        pm   = await message.reply("<b>🥀 𝐏ɤσƈɛssɩŋʛ... 🦋</b>")
        orig = message.reply_to_message
        fresh = await bot.get_messages(orig.chat.id, orig.id)
        media = fresh.video or fresh.audio
        if fresh.audio and getattr(fresh.audio, "file_size", 0) > 100 * 1024 * 1024:
            await pm.edit("❌ ғɪʟᴇ ᴛᴏᴏ ʟᴀʀɢᴇ. ᴍᴀx 100 MB.")
            return
        await pm.edit("<b>⏳ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ…</b>", parse_mode=ParseMode.HTML)
        try:
            fp = await bot.download_media(media)
        except Exception as e:
            await pm.edit(f"❌ {e}")
            return
        thumb = None
        try:
            thumbs = (fresh.video or fresh.audio).thumbs
            if thumbs:
                thumb = await bot.download_media(thumbs[0])
        except Exception:
            pass
        song = {
            "url":              fp,
            "title":            getattr(media, "file_name", "Audio"),
            "duration":         fmt_time(media.duration or 0),
            "duration_seconds": media.duration or 0,
            "requester":        message.from_user.first_name,
            "thumbnail":        thumb,
        }
        add_to_queue(chat_id, song)
        await play_song(chat_id, pm, song)
        return

    match = message.matches[0]
    query = (match.group("q") or "").strip()
    try:
        await message.delete()
    except Exception:
        pass

    # Cooldown check
    now = time.time()
    if chat_id in _last_cmd and (now - _last_cmd[chat_id]) < config.COOLDOWN:
        rem = int(config.COOLDOWN - (now - _last_cmd[chat_id]))
        if chat_id not in _pending:
            rep = await bot.send_message(
                chat_id,
                f"<b>⏳ ᴄᴏᴏʟᴅᴏᴡɴ.</b> ᴘʀᴏᴄᴇssɪɴɢ ɪɴ {rem}s…",
                parse_mode=ParseMode.HTML,
            )
            _pending[chat_id] = (message, rep)
            asyncio.create_task(_run_pending(chat_id, rem))
        return
    _last_cmd[chat_id] = now

    if not query:
        await bot.send_message(
            chat_id,
            "<b>❌ ᴜsᴀɢᴇ :</b> <code>/play &lt;song name or URL&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await _process_play(message, query)


async def _process_play(message: Message, query: str) -> None:
    chat_id = message.chat.id
    pm = await message.reply("<b>🥀 𝐏ɤσƈɛssɩŋʛ... 🦋</b>")

    # Lazy-import to avoid circular at module load
    from ShizuMusic.__main__ import ASSISTANT_USERNAME

    # Check assistant presence
    status = await _is_assistant_in(chat_id, ASSISTANT_USERNAME)
    if status == "banned":
        await pm.edit("<b>❌ ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.</b>", parse_mode=ParseMode.HTML)
        return
    if not status:
        link = await _get_invite(chat_id)
        if not link or not await _invite_assistant(chat_id, link, pm):
            return

    # Normalise youtu.be short links
    if "youtu.be" in query:
        m = re.search(r"youtu\.be/([^?&]+)", query)
        if m:
            query = f"https://www.youtube.com/watch?v={m.group(1)}"

    try:
        result = await search_yt(query)
    except Exception as e:
        await pm.edit(f"<b>❌ sᴇᴀʀᴄʜ ғᴀɪʟᴇᴅ :</b> <code>{e}</code>", parse_mode=ParseMode.HTML)
        return

    # ── Playlist ──────────────────────────────────────────────────────────────
    if isinstance(result, dict) and "playlist" in result:
        items = result["playlist"]
        if not items:
            await pm.edit("<b>❌ ᴇᴍᴘᴛʏ ᴘʟᴀʏʟɪsᴛ</b>", parse_mode=ParseMode.HTML)
            return
        req = message.from_user.first_name if message.from_user else "Unknown"
        first_was_empty = queue_size(chat_id) == 0
        for it in items:
            add_to_queue(chat_id, {
                "url":              it["link"],
                "title":            it["title"],
                "duration":         iso_to_human(it["duration"]),
                "duration_seconds": iso_to_sec(it["duration"]),
                "requester":        req,
                "thumbnail":        it["thumbnail"],
            })
        text = (
            f"<b>✨ ᴀᴅᴅᴇᴅ {len(items)} sᴏɴɢs ᴛᴏ ǫᴜᴇᴜᴇ</b>\n"
            f"<b>❍ #1 :</b> {items[0]['title']}"
        )
        if len(items) > 1:
            text += f"\n<b>❍ #2 :</b> {items[1]['title']}"
        await message.reply(text, parse_mode=ParseMode.HTML)
        if first_was_empty:
            from ShizuMusic.core.queue import peek_current
            first_song = peek_current(chat_id)
            if first_song:
                await play_song(chat_id, pm, first_song)
        else:
            await pm.delete()
        return

    # ── Single track ──────────────────────────────────────────────────────────
    url, title, dur_iso, thumb = result
    if not url:
        await pm.edit("<b>❌ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ. ᴛʀʏ ᴀ ᴅɪғғᴇʀᴇɴᴛ ǫᴜᴇʀʏ.</b>", parse_mode=ParseMode.HTML)
        return

    secs = iso_to_sec(dur_iso)
    if secs > config.MAX_DURATION_SECONDS:
        await pm.edit(
            f"<b>❌ sᴏɴɢ ᴛᴏᴏ ʟᴏɴɢ ({iso_to_human(dur_iso)}).</b>\n"
            f"<i>ᴍᴀx: {config.MAX_DURATION_SECONDS // 60} ᴍɪɴᴜᴛᴇs</i>",
            parse_mode=ParseMode.HTML,
        )
        return

    req  = message.from_user.first_name if message.from_user else "Unknown"
    song = {
        "url":              url,
        "title":            title,
        "duration":         iso_to_human(dur_iso),
        "duration_seconds": secs,
        "requester":        req,
        "thumbnail":        thumb,
    }
    pos = add_to_queue(chat_id, song)

    if pos == 1:
        await play_song(chat_id, pm, song)
    else:
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("⏭ sᴋɪᴩ", callback_data="skip"),
            InlineKeyboardButton("🗑 ᴄʟᴇᴀʀ",  callback_data="clear"),
        ]])
        await message.reply(
            "<b>╭────────────────────▣</b>\n"
            "<b>│✨ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ</b>\n"
            "<b>├────────────────────▣</b>\n"
            f"<b>│❍ ᴛɪᴛʟᴇ :</b> {title}\n"
            f"<b>│❍ ᴅᴜʀ   :</b> {iso_to_human(dur_iso)}\n"
            f"<b>│❍ ʙʏ    :</b> {req}\n"
            f"<b>│❍ ᴩᴏs   :</b> #{pos - 1}\n"
            "<b>╰────────────────────▣</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        await pm.delete()
