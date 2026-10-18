
import os

import streamlit as st
from supabase import create_client
from streamlit_cookies_manager import EncryptedCookieManager


def handle_authentication():
    # ----------------------------------------------
    # SUPABASE CONNECTION
    # ----------------------------------------------

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    try:
        url = url or st.secrets["SUPABASE_URL"]
        key = key or st.secrets["SUPABASE_PUBLISHABLE_KEY"]
    except Exception:
        pass

    if not url or not key:
        st.error(
            "Configure SUPABASE_URL and "
            "SUPABASE_PUBLISHABLE_KEY in your .env "
            "file or Streamlit Secrets."
        )
        st.stop()

    try:
        if "supabase_client" not in st.session_state:
            st.session_state.supabase_client = create_client(
                url.strip().rstrip("/"),
                key.strip(),
            )

        supabase = st.session_state.supabase_client

    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        st.stop()

    # ----------------------------------------------
    # ENCRYPTED LOGIN COOKIES
    # ----------------------------------------------

    cookie_password = os.getenv("COOKIE_PASSWORD")

    try:
        cookie_password = (
            cookie_password or st.secrets["COOKIE_PASSWORD"]
        )
    except Exception:
        pass

    if not cookie_password:
        st.error(
            "Configure COOKIE_PASSWORD in your .env "
            "file or Streamlit Secrets."
        )
        st.stop()

    cookies = EncryptedCookieManager(
        prefix="career_buddy/",
        password=cookie_password,
    )

    if not cookies.ready():
        st.stop()

    # ----------------------------------------------
    # RESTORE LOGIN AFTER REFRESH
    # ----------------------------------------------

    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.get("user"):
        saved_access = cookies.get("sb_access_token")
        saved_refresh = cookies.get("sb_refresh_token")

        if saved_access and saved_refresh:
            try:
                supabase.auth.set_session(
                    saved_access,
                    saved_refresh,
                )

                restored = supabase.auth.get_user()

                if restored and restored.user:
                    st.session_state.user = restored.user

                    current_session = supabase.auth.get_session()

                    if current_session:
                        cookies["sb_access_token"] = (
                            current_session.access_token
                        )
                        cookies["sb_refresh_token"] = (
                            current_session.refresh_token
                        )
                        cookies.save()

            except Exception:
                cookies["sb_access_token"] = ""
                cookies["sb_refresh_token"] = ""
                cookies.save()
                st.session_state.user = None

    # ----------------------------------------------
    # LOGIN AND SIGNUP UI
    # ----------------------------------------------

    if not st.session_state.get("user"):

        st.title("📄 Career Buddy AI")
        st.subheader(
            "Welcome! Please sign in or create an account."
        )

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    key="login_email",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )

                login = st.form_submit_button("Login")

            if login:
                try:
                    result = supabase.auth.sign_in_with_password({
                        "email": email.strip(),
                        "password": password,
                    })

                    if result.user and result.session:
                        st.session_state.user = result.user

                        cookies["sb_access_token"] = (
                            result.session.access_token
                        )
                        cookies["sb_refresh_token"] = (
                            result.session.refresh_token
                        )
                        cookies.save()

                        st.rerun()

                    else:
                        st.error(
                            "Login did not return a valid session."
                        )

                except Exception as e:
                    st.error(f"Login failed: {e}")

        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input(
                    "Email",
                    key="signup_email",
                )
                new_password = st.text_input(
                    "Password",
                    type="password",
                    key="signup_password",
                )

                signup = st.form_submit_button("Create Account")

            if signup:
                if len(new_password) < 8:
                    st.warning(
                        "Use a password with at least 8 characters."
                    )
                else:
                    try:
                        result = supabase.auth.sign_up({
                            "email": new_email.strip(),
                            "password": new_password,
                             "options": {
                                "email_redirect_to": "http://localhost:8501"
                            }
                        })

                        if result.session and result.user:
                            st.session_state.user = result.user

                            cookies["sb_access_token"] = (
                                result.session.access_token
                            )
                            cookies["sb_refresh_token"] = (
                                result.session.refresh_token
                            )
                            cookies.save()

                            st.rerun()

                        else:
                            st.success(
                                "Account created. Check your email "
                                "for confirmation, then log in."
                            )

                    except Exception as e:
                        st.error(f"Sign-up failed: {e}")

        # Stop here until a user is authenticated.
        st.stop()

    return supabase, cookies
