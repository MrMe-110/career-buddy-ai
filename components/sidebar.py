
import uuid
import streamlit as st

from components.styles import apply_theme
from memory_service import load_chat_memory


def _build_chat_archive(recent_user_messages):
    """Group recent messages by conversation session."""
    sessions = {}

    for message in recent_user_messages:
        session_id = message.get("session_id")

        if not session_id:
            continue

        if session_id not in sessions:
            sessions[session_id] = {
                "session_id": session_id,
                "preview": "Previous conversation",
                "search_text": "",
                "latest_at": message.get("created_at", ""),
            }

        content = str(message.get("content", ""))
        sessions[session_id]["search_text"] += " " + content

        # Recent messages normally arrive first.
        if sessions[session_id]["preview"] == "Previous conversation":
            sessions[session_id]["preview"] = content[:65]

    return sorted(
        sessions.values(),
        key=lambda item: str(item["latest_at"]),
        reverse=True,
    )


def render_sidebar(
    supabase,
    cookies,
    user_id,
    saved_resumes,
    recent_user_messages,
):
    """Render settings, resume library, chat history and logout."""

    st.sidebar.success(
        f"Signed in: {st.session_state.user.email}"
    )

    theme = st.sidebar.selectbox(
        "🎨 Appearance",
        ["Light", "Dark"],
        key="app_theme",
    )
    apply_theme(theme)

    st.sidebar.title("📄 Career Buddy")

    model = st.sidebar.selectbox(
        "🤖 AI Model",
        [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
        ],
        key="ai_model",
    )

    temperature = st.sidebar.slider(
        "Creativity",
        min_value=0.1,
        max_value=1.0,
        value=0.7,
        step=0.1,
        key="ai_temperature",
    )

    st.sidebar.divider()

    # Quick prompts
    st.sidebar.subheader("⚡ Quick Prompts")

    quick_prompts = {
        "📝 Build a Resume": (
            "Help me create a professional resume. Ask me for "
            "the information you need."
        ),
        "💼 Interview Preparation": (
            "Help me prepare for a job interview. Give me "
            "common questions and sample answers."
        ),
        "🚀 Improve My Projects": (
            "Help me improve my programming projects for my CV "
            "and portfolio."
        ),
        "🎯 Career Guidance": (
            "Help me choose a suitable career path based on "
            "my skills, interests, and experience."
        ),
    }

    for label, prompt in quick_prompts.items():
        if st.sidebar.button(label, use_container_width=True):
            st.session_state.pending_prompt = prompt
            st.session_state.is_resume_request = False
            st.rerun()

    st.sidebar.divider()

    # Saved resumes
    st.sidebar.subheader("📚 Saved Resumes")

    if saved_resumes:
        resume_options = {
            f"{resume.get('title', 'Untitled Resume')} "
            f"(ID: {resume.get('id', '')})": resume
            for resume in saved_resumes
        }

        selected_label = st.sidebar.selectbox(
            "Choose a resume",
            list(resume_options.keys()),
            key="saved_resume_index",
        )

        selected_resume = resume_options[selected_label]

        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("👁️ View", use_container_width=True):
                st.session_state.last_resume_content = (
                    selected_resume.get("content", "")
                )
                st.session_state.last_resume_title = (
                    selected_resume.get("title", "career_resume")
                )
                st.session_state.show_saved_resume = True
                st.rerun()

        with col2:
            if st.button("✖️ Hide", use_container_width=True):
                st.session_state.show_saved_resume = False
                st.rerun()
    else:
        st.sidebar.caption("No saved resumes yet.")

    st.sidebar.divider()

    # Search and restore conversations
    st.sidebar.subheader("💬 Chat History")

    archive = _build_chat_archive(recent_user_messages)

    search_text = st.sidebar.text_input(
        "Search conversations",
        placeholder="Search your chats...",
    ).strip().lower()

    filtered_archive = [
        item
        for item in archive
        if search_text in (
            item["preview"] + " " + item["search_text"]
        ).lower()
    ]

    if filtered_archive:
        history_options = {
            f"{item['preview']}": item["session_id"]
            for item in filtered_archive
        }

        selected_chat = st.sidebar.selectbox(
            "Previous conversations",
            options=list(history_options.keys()),
            key="history_session_picker",
        )

        if st.sidebar.button(
            "📂 Open Conversation",
            use_container_width=True,
        ):
            session_id = history_options[selected_chat]

            try:
                messages = load_chat_memory(
                    client=supabase,
                    user_id=user_id,
                    session_id=session_id,
                    limit=100,
                )

                st.session_state.messages = messages
                st.session_state.chat_session_id = session_id
                st.session_state.pending_prompt = ""
                st.session_state.last_answer = ""
                st.session_state.is_resume_request = False
                st.rerun()

            except Exception as error:
                st.sidebar.error(
                    f"Could not open conversation: {error}"
                )
    else:
        st.sidebar.caption("No matching conversations found.")

    if st.sidebar.button(
        "➕ Start New Chat",
        use_container_width=True,
    ):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi! 👋 I'm Career Buddy. How can I help you today?"
                ),
            }
        ]
        st.session_state.chat_session_id = str(uuid.uuid4())
        st.session_state.pending_prompt = ""
        st.session_state.last_answer = ""
        st.session_state.is_resume_request = False
        st.session_state.last_resume_content = ""
        st.session_state.show_saved_resume = False
        st.rerun()

    st.sidebar.divider()

    # Logout
    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True,
    ):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        try:
            cookies["sb_access_token"] = ""
            cookies["sb_refresh_token"] = ""
            cookies.save()
        except Exception:
            pass

        keys_to_clear = [
            "user",
            "messages",
            "last_answer",
            "last_resume_content",
            "last_resume_title",
            "show_saved_resume",
            "pending_prompt",
            "chat_session_id",
            "is_resume_request",
            "resume_title",
            "saved_resume_index",
            "history_session_picker",
            "supabase_client",
            "app_theme",
            "ai_model",
            "ai_temperature",
        ]

        for key in keys_to_clear:
            st.session_state.pop(key, None)

        st.rerun()

    return model, temperature
