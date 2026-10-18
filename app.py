
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



supabase, cookies = handle_authentication()



# Check that authentication established a user
if not hasattr(st.session_state, "user") or st.session_state.user is None:
    st.warning("Authentication has not completed. Please sign in.")
    st.stop()

user_id = str(st.session_state.user.id)

st.write("DEBUG 5: User authenticated")

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

st.write("DEBUG 6: Session initialized")

# 3. Load recent chat history
try:
    st.write("DEBUG 7: Loading recent chat history")

    recent_user_messages = load_recent_user_messages(
        client=supabase,
        user_id=user_id,
        limit=500,
    )

    st.write("DEBUG 8: Chat history loaded")

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
                st.write("DEBUG 9: Restoring conversation")

                st.session_state.messages = load_chat_memory(
                    client=supabase,
                    user_id=user_id,
                    session_id=session_id,
                    limit=100,
                )

                st.session_state.chat_session_id = session_id

                st.write("DEBUG 10: Conversation restored")

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

st.write("DEBUG 11: Message state ready")

# 5. Load only this user's saved resumes
try:
    st.write("DEBUG 12: Loading saved resumes")

    saved_resumes = get_resumes(
        client=supabase,
        user_id=user_id,
        limit=50,
    )

    st.write("DEBUG 13: Saved resumes loaded")

except Exception as error:
    saved_resumes = []
    st.sidebar.warning(f"Could not load saved resumes: {error}")

# 6. Check the Groq API configuration
try:
    st.write("DEBUG 14: Checking AI configuration")

    get_groq_api_key()

    st.write("DEBUG 15: AI configuration checked")

except Exception as error:
    st.error(f"AI configuration error: {error}")
    st.stop()

# 7. Render the sidebar
st.write("DEBUG 16: Rendering sidebar")

model, temperature = render_sidebar(
    supabase=supabase,
    cookies=cookies,
    user_id=user_id,
    saved_resumes=saved_resumes,
    recent_user_messages=recent_user_messages,
)

st.write("DEBUG 17: Sidebar rendered")

# 8. Render the main application
st.write("DEBUG 18: Rendering main content")

render_main_content(
    supabase=supabase,
    user_id=user_id,
    model=model,
    temperature=temperature,
)

st.write("DEBUG 19: Main content rendered")
