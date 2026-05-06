"""
ShizuMusic/core/call.py
Voice chat helpers — join, leave, stream ended handler.
"""
import asyncio

from pyrogram.enums import ParseMode
from pytgcalls import filters as fl
from pytgcalls.types.stream import StreamEnded

from ShizuMusic import LOGGER, bot, call_py
from ShizuMusic.core.queue import clear_queue, peek_current, pop_current
from ShizuMusic.utils.helpers import delete_file


async def leave_vc(chat_id: int) -> None:
    """Leave voice chat and clean up queue files."""
    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass
    for song in clear_queue(chat_id):
        delete_file(song.get("file_path", ""))


@call_py.on_update(fl.stream_end())
async def on_stream_end(_: object, update: StreamEnded) -> None:
    """Auto-play next song when current stream ends."""
    chat_id = update.chat_id
    done = pop_current(chat_id)
    if done:
        await asyncio.sleep(2)
        delete_file(done.get("file_path", ""))

    nxt = peek_current(chat_id)
    if nxt:
        # Import here to avoid circular import
        from ShizuMusic.core.player import play_song
        try:
            msg = await bot.send_message(
                chat_id,
                f"<b>🎧 ɴᴇxᴛ :</b> {nxt['title']}",
                parse_mode=ParseMode.HTML,
            )
            await play_song(chat_id, msg, nxt)
        except Exception as e:
            await bot.send_message(chat_id, f"❌ {e}")
    else:
        await leave_vc(chat_id)
        await bot.send_message(
            chat_id,
            "<b>✅ ǫᴜᴇᴜᴇ ғɪɴɪsʜᴇᴅ.</b>",
            parse_mode=ParseMode.HTML,
        )
