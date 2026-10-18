
from database import (
    get_messages,
    get_user_chat_history,
    save_message,
    delete_chat_session,
)


def save_chat_message(client, user_id, session_id, role, content):
    return save_message(
        client=client,
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
    )


def load_chat_memory(client, user_id, session_id, limit=30):
    rows = get_messages(
        client=client,
        user_id=user_id,
        session_id=session_id,
        limit=limit,
    )

    return [
        {
            "role": row["role"],
            "content": row["content"],
        }
        for row in rows
        if row.get("role") in ("user", "assistant")
        and row.get("content")
    ]


def load_recent_user_messages(client, user_id, limit=100):
    rows = get_user_chat_history(
        client=client,
        user_id=user_id,
        limit=limit,
    )

    return [
        {
            "role": row["role"],
            "content": row["content"],
            "session_id": row.get("session_id"),
            "created_at": row.get("created_at"),
        }
        for row in rows
        if row.get("role") in ("user", "assistant")
        and row.get("content")
    ]


def clear_chat_memory(client, user_id, session_id):
    return delete_chat_session(
        client=client,
        user_id=user_id,
        session_id=session_id,
    )


def build_resume_context(resume):
    if not resume:
        return ""

    title = resume.get("title", "Untitled Resume")
    content = resume.get("content", "")

    if not content:
        return ""

    return (
        f"Current resume title: {title}\n\n"
        "Use this saved resume when the user asks to revise it. "
        "Preserve the user's real qualifications and never invent "
        "skills, experience, education, or achievements.\n\n"
        f"{content}"
    )
