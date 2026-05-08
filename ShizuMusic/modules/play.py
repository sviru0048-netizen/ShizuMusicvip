# --------------------------------------------------------------------------------
#  ShizuMusic © 2026
#  Developed by Bad Munda ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio
import re
import time

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    RPCError,
    UserAlreadyParticipant,
)
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import config
from ShizuMusic import bot
from ShizuMusic.core.player import play_song
from ShizuMusic.core.queue import (
    add_to_queue,
    peek_current,
    queue_size,
)
from ShizuMusic.utils.formatters import (
    fmt_time,
    iso_to_human,
    iso_to_sec,
    short,
)
from ShizuMusic.utils.youtube import search_yt


# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
_last_cmd: dict[int, float] = {}
_pending:  dict[int, tuple] = {}


# ─────────────────────────────────────────────
# DB HELPER
# ─────────────────────────────────────────────
def _db_track(chat_id: int, user_id: int) -> None:
    try:
        from ShizuMusic.database import add_served_chat, add_served_user
        add_served_chat(chat_id)
        if user_id:
            add_served_user(user_id)
    except Exception:
        pass


# ─────────────────────────────────────────────
# ASSISTANT HELPERS
# ─────────────────────────────────────────────
async def _get_invite(chat_id: int) -> str | None:

    try:
        chat = await bot.get_chat(chat_id)

        return (
            chat.invite_link
            or (
                f"https://t.me/{chat.username}"
                if chat.username
                else None
            )
        )

    except Exception:
        return None


async def _is_assistant_in(
    chat_id: int,
    assistant_username: str,
):

    from ShizuMusic import assistant

    try:
        member = await assistant.get_chat_member(
            chat_id,
            assistant_username,
        )

        return member.status is not None

    except Exception as e:

        err = str(e)

        if (
            "USER_BANNED" in err
            or "Banned" in err
        ):
            return "banned"

        return False


async def _invite_assistant(
    chat_id: int,
    link: str,
    msg: Message,
) -> bool:

    from ShizuMusic import assistant

    try:

        await assistant.join_chat(link)

        return True

    except UserAlreadyParticipant:

        return True

    except RPCError as e:

        await msg.edit_text(
            f"""
<b>❍ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴ ғᴀɪʟᴇᴅ</b><code>{e.error_message}</code>
""",
            parse_mode=ParseMode.HTML,
        )

        return False

    except Exception as e:

        await msg.edit_text(
            f"""
<b>❍ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴ ғᴀɪʟᴇᴅ</b>

<code>{e}</code>
""",
            parse_mode=ParseMode.HTML,
        )

        return False


# ─────────────────────────────────────────────
# COOLDOWN HANDLER
# ─────────────────────────────────────────────
async def _run_pending(
    chat_id: int,
    delay: int,
) -> None:

    await asyncio.sleep(delay)

    if chat_id in _pending:

        msg, reply = _pending.pop(chat_id)

        try:
            await reply.delete()

        except Exception:
            pass

        await play_handler(bot, msg)


# ─────────────────────────────────────────────
# PLAY COMMAND
# ─────────────────────────────────────────────
@bot.on_message(
    filters.group
    & filters.regex(
        r"^/play(?:@\w+)?(?:\s+(?P<q>.+))?$"
    )
)
async def play_handler(_, message: Message) -> None:

    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0

    # DB — track chat & user
    _db_track(chat_id, user_id)

    # ─────────────────────────────────────────
    # REPLIED AUDIO / VIDEO
    # ─────────────────────────────────────────
    if (
        message.reply_to_message
        and (
            message.reply_to_message.audio
            or message.reply_to_message.video
        )
    ):

        pm = await message.reply(
            """
<b>❍ ᴘʀᴏᴄᴇssɪɴɢ ᴍᴇᴅɪᴀ...</b>
""",
            parse_mode=ParseMode.HTML,
        )

        orig = message.reply_to_message

        fresh = await bot.get_messages(
            orig.chat.id,
            orig.id,
        )

        media = fresh.video or fresh.audio

        # File Limit
        if (
            fresh.audio
            and getattr(
                fresh.audio,
                "file_size",
                0,
            ) > 100 * 1024 * 1024
        ):

            await pm.edit_text(
                """
<b>❍ ғɪʟᴇ ᴛᴏᴏ ʟᴀʀɢᴇ</b>
<b>❍ ᴍᴀx sɪᴢᴇ :</b>
<code>100 MB</code>
""",
                parse_mode=ParseMode.HTML,
            )
            return

        await pm.edit_text(
            """
<b>❍ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴍᴇᴅɪᴀ...</b>
""",
            parse_mode=ParseMode.HTML,
        )

        try:

            fp = await bot.download_media(media)

        except Exception as e:

            await pm.edit_text(
                f"""
<b>❍ ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ</b>
<code>{e}</code>
""",
                parse_mode=ParseMode.HTML,
            )
            return

        thumb = None

        try:

            thumbs = (
                fresh.video
                or fresh.audio
            ).thumbs

            if thumbs:
                thumb = await bot.download_media(
                    thumbs[0]
                )

        except Exception:
            pass

        song = {
            "url": fp,
            "title": getattr(
                media,
                "file_name",
                "Audio",
            ),
            "duration": fmt_time(
                media.duration or 0
            ),
            "duration_seconds": (
                media.duration or 0
            ),
            "requester": (
                message.from_user.first_name
                if message.from_user
                else "Unknown"
            ),
            "requester_id": user_id,   # DB tracking
            "thumbnail": thumb,
        }

        add_to_queue(chat_id, song)

        await play_song(chat_id, pm, song)

        return

    # ─────────────────────────────────────────
    # QUERY
    # ─────────────────────────────────────────
    match = message.matches[0]

    query = (
        match.group("q") or ""
    ).strip()

    try:
        await message.delete()

    except Exception:
        pass

    # ─────────────────────────────────────────
    # COOLDOWN
    # ─────────────────────────────────────────
    now = time.time()

    if (
        chat_id in _last_cmd
        and (
            now - _last_cmd[chat_id]
        ) < config.COOLDOWN
    ):

        rem = int(
            config.COOLDOWN
            - (
                now
                - _last_cmd[chat_id]
            )
        )

        if chat_id not in _pending:

            rep = await bot.send_message(
                chat_id,
                f"""
<b>❍ ᴄᴏᴏʟᴅᴏᴡɴ ᴀᴄᴛɪᴠᴇ</b>
<b>❍ ᴘʀᴏᴄᴇssɪɴɢ ɪɴ :</b>
<code>{rem}s</code>
""",
                parse_mode=ParseMode.HTML,
            )

            _pending[chat_id] = (
                message,
                rep,
            )

            asyncio.create_task(
                _run_pending(
                    chat_id,
                    rem,
                )
            )

        return

    _last_cmd[chat_id] = now

    # ─────────────────────────────────────────
    # EMPTY QUERY
    # ─────────────────────────────────────────
    if not query:

        await bot.send_message(
            chat_id,
            """
<b>❍ ɪɴᴠᴀʟɪᴅ ᴜsᴀɢᴇ</b>
<b>❍ ᴜsᴇ :</b><code>/play song name</code><code>/play youtube url</code>
""",
            parse_mode=ParseMode.HTML,
        )

        return

    await _process_play(
        message,
        query,
    )


# ─────────────────────────────────────────────
# PROCESS PLAY
# ─────────────────────────────────────────────
async def _process_play(
    message: Message,
    query: str,
) -> None:

    chat_id = message.chat.id

    pm = await message.reply(
        """
<b>❍ ᴘʀᴏᴄᴇssɪɴɢ...</b>
""",
        parse_mode=ParseMode.HTML,
    )

    # Avoid circular import — runtime import
    try:
        from ShizuMusic.__main__ import ASSISTANT_USERNAME
    except Exception:
        ASSISTANT_USERNAME = ""

    # ─────────────────────────────────────────
    # ASSISTANT CHECK
    # ─────────────────────────────────────────
    if ASSISTANT_USERNAME:

        status = await _is_assistant_in(
            chat_id,
            ASSISTANT_USERNAME,
        )

        if status == "banned":

            await pm.edit_text(
                """
<b>❍ ᴀssɪsᴛᴀɴᴛ ʙᴀɴɴᴇᴅ</b>
<b>❍ ᴜɴʙᴀɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>
""",
                parse_mode=ParseMode.HTML,
            )

            return

        if not status:

            link = await _get_invite(chat_id)

            if (
                not link
                or not await _invite_assistant(
                    chat_id,
                    link,
                    pm,
                )
            ):
                return

    # ─────────────────────────────────────────
    # NORMALISE YOUTU.BE
    # ─────────────────────────────────────────
    if "youtu.be" in query:

        match = re.search(
            r"youtu\.be/([^?&]+)",
            query,
        )

        if match:

            query = (
                "https://www.youtube.com/watch?v="
                f"{match.group(1)}"
            )

    # ─────────────────────────────────────────
    # SEARCH
    # ─────────────────────────────────────────
    try:

        result = await search_yt(query)

    except Exception as e:

        await pm.edit_text(
            f"""
<b>❍ sᴇᴀʀᴄʜ ғᴀɪʟᴇᴅ</b><code>{e}</code>
""",
            parse_mode=ParseMode.HTML,
        )

        return

    # ─────────────────────────────────────────
    # PLAYLIST
    # ─────────────────────────────────────────
    if (
        isinstance(result, dict)
        and "playlist" in result
    ):

        items = result["playlist"]

        if not items:

            await pm.edit_text(
                """
<b>❍ ᴇᴍᴘᴛʏ ᴘʟᴀʏʟɪsᴛ</b>
<b>❍ ɴᴏ sᴏɴɢs ғᴏᴜɴᴅ.</b>
""",
                parse_mode=ParseMode.HTML,
            )

            return

        req    = message.from_user.first_name if message.from_user else "Unknown"
        req_id = message.from_user.id if message.from_user else 0

        first_was_empty = (
            queue_size(chat_id) == 0
        )

        for item in items:

            add_to_queue(
                chat_id,
                {
                    "url": item["link"],
                    "title": item["title"],
                    "duration": iso_to_human(
                        item["duration"]
                    ),
                    "duration_seconds": iso_to_sec(
                        item["duration"]
                    ),
                    "requester":    req,
                    "requester_id": req_id,   # DB tracking
                    "thumbnail": item["thumbnail"],
                },
            )

        text = f"""
<b>❍ ᴘʟᴀʏʟɪsᴛ ᴀᴅᴅᴇᴅ</b>
<b>❍ sᴏɴɢs :</b><code>{len(items)}</code>
<b>❍ ғɪʀsᴛ ᴛʀᴀᴄᴋ :</b><code>{short(items[0]['title'])}</code>
"""

        if len(items) > 1:

            text += f"""

<b>❍ sᴇᴄᴏɴᴅ ᴛʀᴀᴄᴋ :</b>
<code>{short(items[1]['title'])}</code>
"""

        await message.reply(
            text,
            parse_mode=ParseMode.HTML,
        )

        if first_was_empty:

            first_song = peek_current(chat_id)

            if first_song:

                await play_song(
                    chat_id,
                    pm,
                    first_song,
                )

        else:

            await pm.delete()

        return

    # ─────────────────────────────────────────
    # SINGLE TRACK
    # ─────────────────────────────────────────
    url, title, dur_iso, thumb = result

    if not url:

        await pm.edit_text(
            """
<b>❍ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ</b>
<b>❍ ᴛʀʏ ᴀɴᴏᴛʜᴇʀ ǫᴜᴇʀʏ.</b>
""",
            parse_mode=ParseMode.HTML,
        )

        return

    secs = iso_to_sec(dur_iso)

    if secs > config.MAX_DURATION_SECONDS:

        await pm.edit_text(
            f"""
<b>❍ sᴏɴɢ ᴛᴏᴏ ʟᴏɴɢ</b>
<b>❍ ᴅᴜʀᴀᴛɪᴏɴ :</b><code>{iso_to_human(dur_iso)}</code>
<b>❍ ᴍᴀx ʟɪᴍɪᴛ :</b>
<code>{config.MAX_DURATION_SECONDS // 60} min</code>
""",
            parse_mode=ParseMode.HTML,
        )

        return

    req    = message.from_user.first_name if message.from_user else "Unknown"
    req_id = message.from_user.id if message.from_user else 0

    song = {
        "url":              url,
        "title":            title,
        "duration":         iso_to_human(dur_iso),
        "duration_seconds": secs,
        "requester":        req,
        "requester_id":     req_id,   # DB tracking
        "thumbnail":        thumb,
    }

    pos = add_to_queue(
        chat_id,
        song,
    )

    # ─────────────────────────────────────────
    # PLAY NOW
    # ─────────────────────────────────────────
    if pos == 1:

        await play_song(
            chat_id,
            pm,
            song,
        )

    # ─────────────────────────────────────────
    # ADD TO QUEUE
    # ─────────────────────────────────────────
    else:

        kb = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "⌯ sᴋɪᴘ ⌯",
                    callback_data="skip",
                ),
                InlineKeyboardButton(
                    "⌯ ᴄʟᴇᴀʀ ⌯",
                    callback_data="clear",
                ),
            ]]
        )

        await message.reply(
            f"""
<b>❍ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ</b>
<b>❍ ᴛɪᴛʟᴇ :</b><code>{short(title)}</code>
<b>❍ ᴅᴜʀᴀᴛɪᴏɴ :</b><code>{iso_to_human(dur_iso)}</code>
<b>❍ ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b><code>{req}</code>
<b>❍ ᴘᴏsɪᴛɪᴏɴ :</b><code>#{pos - 1}</code>
""",
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )

        await pm.delete()
