"""
ShizuMusic/core/queue.py
In-memory queue management for each chat.
"""

# chat_id → list of song dicts
chat_queues: dict[int, list] = {}


def get_queue(chat_id: int) -> list:
    return chat_queues.get(chat_id, [])


def add_to_queue(chat_id: int, song: dict) -> int:
    """Add song to queue. Returns new queue length."""
    chat_queues.setdefault(chat_id, []).append(song)
    return len(chat_queues[chat_id])


def pop_current(chat_id: int) -> dict | None:
    """Remove and return the first song in queue."""
    q = chat_queues.get(chat_id)
    if q:
        return q.pop(0)
    return None


def peek_current(chat_id: int) -> dict | None:
    """Return first song without removing."""
    q = chat_queues.get(chat_id)
    return q[0] if q else None


def peek_next(chat_id: int) -> dict | None:
    """Return second song without removing."""
    q = chat_queues.get(chat_id)
    return q[1] if q and len(q) > 1 else None


def clear_queue(chat_id: int) -> list:
    """Clear queue and return all removed songs."""
    return chat_queues.pop(chat_id, [])


def queue_size(chat_id: int) -> int:
    return len(chat_queues.get(chat_id, []))
