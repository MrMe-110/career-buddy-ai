import re
import time
import streamlit as st

from ai_chain import generate_answer
from database import save_messages, save_resume, get_resumes
from resume_generator import create_docx, format_resume_for_display


def _render_header():
    st.markdown(
        """
        <div class="hero">
            <h1>📄 Career Buddy AI</h1>
            <p>Your AI assistant for resumes, careers, projects, and interviews.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📝 Resume Builder</h3>
                <p>Create a professional resume with AI assistance.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>💬 AI Career Chat</h3>
                <p>Get career advice and improve your skills.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🎯 Interview Preparation</h3>
                <p>Practice questions and prepare for opportunities.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_resume_builder():
    with st.expander("📝 Build a Resume", expanded=False):
        with st.form("resume_builder_form"):
            full_name = st.text_input("Full Name")
            target_role = st.text_input(
                "Target Job Role",
                placeholder="e.g. Front-End Developer",
            )
            education = st.text_area(
                "Education",
                placeholder="Degree, institution, graduation year...",
            )
            skills = st.text_area(
                "Skills",
                placeholder="HTML, CSS, Python...",
            )
            projects = st.text_area(
                "Projects",
                placeholder="Project names and what you built...",
            )
            experience = st.text_area(
                "Work Experience",
                placeholder="Internships, jobs, or relevant experience...",
            )

            submitted = st.form_submit_button(
                "✨ Generate My Resume",
                use_container_width=True,
            )

        if submitted:
            if not full_name.strip() or not target_role.strip():
                st.warning("Please enter your name and target job role.")
                return

            if not any(
                value.strip()
                for value in [education, skills, projects, experience]
            ):
                st.warning(
                    "Please provide at least one section: education, "
                    "skills, projects, or experience."
                )
                return

            prompt = f"""
Create a professional, ATS-friendly resume using the information below.

IMPORTANT:
- Do not invent qualifications, employment, dates, or achievements.
- Use clear professional language.
- Keep the resume suitable for the target role.
- Use headings and bullet points.
- If information is missing, do not fabricate it.

Full Name: {full_name}
Target Job Role: {target_role}
Education: {education}
Skills: {skills}
Projects: {projects}
Work Experience: {experience}

Return the complete resume content.
"""

            st.session_state.pending_prompt = prompt
            st.session_state.resume_title = (
                f"{full_name.strip()} - {target_role.strip()}"
            )
            st.session_state.is_resume_request = True
            st.session_state.show_saved_resume = False
            st.session_state.last_resume_content = ""
            st.rerun()


def _save_chat_pair(supabase, user_id, session_id, user_prompt, answer):
    """Save the user prompt and assistant response."""
    save_messages(
        client=supabase,
        user_id=user_id,
        session_id=session_id,
        messages=[
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": answer},
        ],
    )


def _get_saved_resumes(supabase, user_id):
    """Retrieve saved resumes belonging to the authenticated user."""
    try:
        resumes = get_resumes(
            client=supabase,
            user_id=user_id,
            limit=50,
        )
        return resumes or []

    except Exception as error:
        st.warning(f"Could not retrieve your saved resumes: {error}")
        return []


def _find_saved_resume(supabase, user_id, prompt):
    """
    Search saved resumes by title and content.
    If no clear match exists, use the latest saved resume.
    """
    resumes = _get_saved_resumes(supabase, user_id)

    if not resumes:
        return None

    prompt_lower = prompt.lower()

    # Ignore common words that do not help identify a resume.
    stop_words = {
        "show", "give", "find", "open", "display", "retrieve",
        "download", "please", "resume", "resumes", "about",
        "latest", "previous", "saved", "created", "my", "the",
        "last", "me", "can", "you", "for", "from", "with",
        "this", "that", "want", "need", "get", "cv",
    }

    keywords = {
        word.strip(".,?!:;()[]{}\"'").lower()
        for word in prompt_lower.split()
    }

    keywords = {
        word for word in keywords
        if len(word) > 2 and word not in stop_words
    }

    best_resume = None
    best_score = 0

    for resume in resumes:
        title = str(resume.get("title", "") or "").lower()
        content = str(resume.get("content", "") or "").lower()

        score = 0

        for keyword in keywords:
            if keyword in title:
                score += 5
            elif keyword in content:
                score += 1

        if score > best_score:
            best_score = score
            best_resume = resume

    # If no keywords match, fall back to the latest saved resume.
    if best_resume is None:
        best_resume = max(
            resumes,
            key=lambda resume: str(
                resume.get("updated_at")
                or resume.get("created_at")
                or ""
            ),
        )

    return best_resume


def _asks_for_saved_resume(prompt):
    """Recognize common requests to retrieve an existing resume."""
    text = prompt.lower()

    resume_terms = (
        "resume",
        "resumes",
        "cv",
        "curriculum vitae",
    )

    retrieval_terms = (
        "last",
        "latest",
        "previous",
        "saved",
        "created",
        "show",
        "give",
        "retrieve",
        "open",
        "display",
        "my resume",
        "my cv",
        "download",
        "find",
        "search",
        "get",
    )

    return (
        any(term in text for term in resume_terms)
        and any(term in text for term in retrieval_terms)
    )


def _process_prompt(
    supabase,
    user_id,
    model,
    temperature,
    prompt,
):
    is_resume = st.session_state.get("is_resume_request", False)
    resume_title = st.session_state.get("resume_title", "My Resume")

    st.session_state.pending_prompt = ""
    st.session_state.is_resume_request = False

    # Search saved resumes when the user requests a previous resume.
    selected_resume = None

    if _asks_for_saved_resume(prompt) and not is_resume:
        selected_resume = _find_saved_resume(
            supabase,
            user_id,
            prompt,
        )

    # For ordinary questions, provide the latest resume as context.
    if selected_resume is None:
        resumes = _get_saved_resumes(supabase, user_id)

        if resumes:
            selected_resume = max(
                resumes,
                key=lambda resume: str(
                    resume.get("updated_at")
                    or resume.get("created_at")
                    or ""
                ),
            )

    saved_resume_content = ""
    saved_resume_title = ""

    if selected_resume:
        saved_resume_content = (
            selected_resume.get("content", "") or ""
        )
        saved_resume_title = (
            selected_resume.get("title", "My Resume") or "My Resume"
        )

    # Use the saved resume, or a resume created during the current session.
    current_resume = (
        saved_resume_content
        or st.session_state.get("last_resume_content", "")
    )

    current_resume_title = (
        saved_resume_title
        or st.session_state.get("last_resume_title", "My Resume")
    )

    original_prompt = prompt

    # Supply the actual saved resume explicitly to the AI.
    if _asks_for_saved_resume(original_prompt) and not is_resume:
        if current_resume:
            prompt = f"""
The user wants to retrieve a previously saved resume.

Selected resume title: {current_resume_title}

Instructions:
- Return the complete resume when the user asks to see or download it.
- Preserve the saved content and personal information.
- Do not invent qualifications or achievements.
- Do not claim that a resume was saved unless the database confirms it.

Saved resume content:
{current_resume}

User's original request:
{original_prompt}
"""
        else:
            prompt = f"""
No saved resume was found in the user's account.

Do not invent a previous resume or claim that one exists.
Explain politely that no saved resume could be found and suggest
using the Resume Builder.

User's original request:
{original_prompt}
"""

    # Store the original user message rather than the internal context.
    st.session_state.messages.append(
        {"role": "user", "content": original_prompt}
    )

    with st.chat_message("user"):
        st.markdown(original_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Career Buddy is thinking..."):
            start_time = time.time()
            conversation_history = st.session_state.messages[:-1]

            try:
                answer = generate_answer(
                    prompt=prompt,
                    messages=conversation_history,
                    model=model,
                    temperature=temperature,
                    current_resume=current_resume,
                )

                if not isinstance(answer, str):
                    answer = str(answer)

            except Exception as error:
                st.error(f"Could not generate a response: {error}")
                st.session_state.messages.pop()
                return

            elapsed = time.time() - start_time

        st.markdown(answer)
        st.caption(f"⏱️ Response time: {elapsed:.2f} seconds")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
    st.session_state.last_answer = answer

    # Display the newly generated resume.
    if is_resume:
        st.session_state.last_resume_content = answer
        st.session_state.last_resume_title = resume_title
        st.session_state.show_saved_resume = True

    # Save the original conversation, not the augmented internal prompt.
    try:
        _save_chat_pair(
            supabase=supabase,
            user_id=user_id,
            session_id=st.session_state.chat_session_id,
            user_prompt=original_prompt,
            answer=answer,
        )
    except Exception as error:
        st.warning(
            f"Response generated, but chat history was not saved: {error}"
        )

    # Save newly generated resumes to Supabase.
    if is_resume:
        try:
            save_resume(
                client=supabase,
                user_id=user_id,
                title=resume_title,
                content=answer,
            )
            st.success("Resume generated and saved successfully!")
        except Exception as error:
            st.warning(
                f"Resume generated, but it could not be saved: {error}"
            )

        st.rerun()

    # Show the selected saved resume in the download section.
    elif _asks_for_saved_resume(original_prompt) and current_resume:
        st.session_state.last_resume_content = current_resume
        st.session_state.last_resume_title = current_resume_title
        st.session_state.show_saved_resume = True


def _render_resume_download():
    if not st.session_state.get("show_saved_resume", False):
        return

    resume_content = st.session_state.get("last_resume_content", "")

    if not resume_content:
        return

    st.divider()
    st.subheader("📄 Your Resume")

    try:
        formatted_resume = format_resume_for_display(resume_content)
        st.markdown(formatted_resume, unsafe_allow_html=True)
    except Exception:
        st.markdown(resume_content)

    title = st.session_state.get("last_resume_title", "career_resume")

    safe_filename = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        title,
    ).strip("_")

    if not safe_filename:
        safe_filename = "career_resume"

    try:
        docx_file = create_docx(resume_content)

        st.download_button(
            label="⬇️ Download Resume as DOCX",
            data=docx_file,
            file_name=f"{safe_filename}.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            key="download_resume_docx",
        )
    except Exception as error:
        st.warning(f"Could not create the DOCX file: {error}")


def render_main_content(supabase, user_id, model, temperature):
    _render_header()

    st.write("")
    _render_resume_builder()

    st.divider()
    st.subheader("💬 Chat with Career Buddy")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    typed_prompt = st.chat_input(
        "Ask about your resume, career, projects, or interviews..."
    )

    pending_prompt = st.session_state.get("pending_prompt", "")

    if typed_prompt:
        st.session_state.is_resume_request = False
        prompt_to_process = typed_prompt
    else:
        prompt_to_process = pending_prompt

    if prompt_to_process:
        _process_prompt(
            supabase=supabase,
            user_id=user_id,
            model=model,
            temperature=temperature,
            prompt=prompt_to_process,
        )

    _render_resume_download()

    st.divider()
    st.caption(
        "Career Buddy AI | Built with Streamlit, LangChain, Groq, and Supabase"
    )
