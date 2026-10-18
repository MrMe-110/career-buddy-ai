
import uuid

import streamlit as st
from dotenv import load_dotenv

from components.auth import handle_authentication
from components.sidebar import render_sidebar
from components.chat_ui import render_main_content

from ai_chain import get_groq_api_key
from database import get_resumes
from memory_service import load_chat_memory, load_recent_user_messages


load_dotenv()

st.set_page_config(
    page_title="Career Buddy AI",
    page_icon="📄",
    layout="wide",
)

# 1. Authenticate the user
supabase, cookies = handle_authentication()
user_id = str(st.session_state.user.id)

# 2. Initialize session variables
defaults = {
    "pending_prompt": "",
    "last_answer": "",
    "is_resume_request": False,
    "last_resume_content": "",
    "last_resume_title": "career_resume",
    "show_saved_resume": False,
    "resume_title": "My Resume",
    "chat_session_id": str(uuid.uuid4()),
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 3. Load recent chat history
try:
    recent_user_messages = load_recent_user_messages(
        client=supabase,
        user_id=user_id,
        limit=500,
    )
except Exception as error:
    recent_user_messages = []
    st.warning(f"Could not load chat history: {error}")

# 4. Restore the most recent conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

    if recent_user_messages:
        session_id = recent_user_messages[0].get("session_id")

        if session_id:
            try:
                st.session_state.messages = load_chat_memory(
                    client=supabase,
                    user_id=user_id,
                    session_id=session_id,
                    limit=100,
                )
                st.session_state.chat_session_id = session_id
            except Exception as error:
                st.warning(f"Could not restore conversation: {error}")

    if not st.session_state.messages:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi! 👋 I'm Career Buddy. I can help you build a "
                    "professional resume, improve your projects, and "
                    "prepare for job opportunities."
                ),
            }
        ]

# 5. Load only this user's saved resumes
try:
    saved_resumes = get_resumes(
        client=supabase,
        user_id=user_id,
        limit=50,
    )
except Exception as error:
    saved_resumes = []
    st.sidebar.warning(f"Could not load saved resumes: {error}")

# 6. Check the Groq API configuration
try:
    get_groq_api_key()
except Exception as error:
    st.error(f"AI configuration error: {error}")
    st.stop()

# 7. Render the sidebar
model, temperature = render_sidebar(
    supabase=supabase,
    cookies=cookies,
    user_id=user_id,
    saved_resumes=saved_resumes,
    recent_user_messages=recent_user_messages,
)

# 8. Render the main application
render_main_content(
    supabase=supabase,
    user_id=user_id,
    model=model,
    temperature=temperature,
)
