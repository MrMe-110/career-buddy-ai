
from datetime import datetime, timezone


# ==================================================
# RESUME OPERATIONS
# ==================================================

def save_resume(client, user_id, title, content):
    if not user_id:
        raise ValueError("A valid user ID is required.")

    if not title.strip() or not content.strip():
        raise ValueError("Resume title and content cannot be empty.")

    return (
        client.table("resumes")
        .insert({
            "user_id": user_id,
            "title": title.strip(),
            "content": content.strip(),
        })
        .execute()
    )


def get_resumes(client, user_id, limit=50):
    if not user_id:
        return []

    response = (
        client.table("resumes")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .limit(max(1, min(int(limit), 200)))
        .execute()
    )

    return response.data or []


def get_resume(client, user_id, resume_id):
    if not user_id:
        return None

    response = (
        client.table("resumes")
        .select("*")
        .eq("user_id", user_id)
        .eq("id", resume_id)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


def update_resume(client, user_id, resume_id, title, content):
    if not user_id:
        raise ValueError("A valid user ID is required.")

    if not title.strip() or not content.strip():
        raise ValueError("Resume title and content cannot be empty.")

    return (
        client.table("resumes")
        .update({
            "title": title.strip(),
            "content": content.strip(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("user_id", user_id)
        .eq("id", resume_id)
        .execute()
    )


def delete_resume(client, user_id, resume_id):
    if not user_id:
        raise ValueError("A valid user ID is required.")

    return (
        client.table("resumes")
        .delete()
        .eq("user_id", user_id)
        .eq("id", resume_id)
        .execute()
    )


# ==================================================
# CHAT MESSAGE OPERATIONS
# ==================================================

def save_message(client, user_id, session_id, role, content):
    if not user_id or not session_id:
        raise ValueError("A valid user ID and session ID are required.")

    if role not in ("user", "assistant"):
        raise ValueError("Role must be 'user' or 'assistant'.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Message content cannot be empty.")

    return (
        client.table("chat_messages")
        .insert({
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "content": content,
        })
        .execute()
    )


def save_messages(client, user_id, session_id, messages):
    if not user_id or not session_id:
        raise ValueError("A valid user ID and session ID are required.")

    rows = []

    for message in messages:
        role = message.get("role")
        content = message.get("content", "")

        if role not in ("user", "assistant"):
            continue

        if not isinstance(content, str) or not content.strip():
            continue

        rows.append({
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "content": content,
        })

    if not rows:
        return None

    return client.table("chat_messages").insert(rows).execute()


def get_messages(client, user_id, session_id, limit=500):
    if not user_id or not session_id:
        return []

    limit = max(1, min(int(limit), 1000))

    response = (
        client.table("chat_messages")
        .select("*")
        .eq("user_id", user_id)
        .eq("session_id", session_id)
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )

    return response.data or []


def get_user_chat_history(client, user_id, limit=500):
    if not user_id:
        return []

    limit = max(1, min(int(limit), 1000))

    response = (
        client.table("chat_messages")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def delete_chat_session(client, user_id, session_id):
    if not user_id or not session_id:
        raise ValueError("A valid user ID and session ID are required.")

    return (
        client.table("chat_messages")
        .delete()
        .eq("user_id", user_id)
        .eq("session_id", session_id)
        .execute()
    )
