
import streamlit as st


def apply_theme(theme="Light"):
    if theme == "Dark":
        bg = "#0E1117"
        text_color = "#F1F5F2"
        heading_color = "#B7E4C7"
        card_bg = "#1C2230"
        sidebar_bg = "#151B24"
        border_color = "#354238"
        input_bg = "#222B36"
        muted_color = "#C0CCC4"
    else:
        bg = "#F5F7F4"
        text_color = "#26382C"
        heading_color = "#244B36"
        card_bg = "#FFFFFF"
        sidebar_bg = "#EAF0E8"
        border_color = "#DCE5DC"
        input_bg = "#FFFFFF"
        muted_color = "#526357"

    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg};
        color: {text_color};
    }}

    .stApp h1, .stApp h2, .stApp h3 {{
        color: {heading_color} !important;
    }}

    .stApp p, .stApp label,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stWidgetLabel"] {{
        color: {text_color};
    }}

    .hero {{
        background-color: #244B36;
        color: #FFFFFF;
        padding: 30px;
        border-radius: 18px;
        margin-bottom: 20px;
    }}

    .hero h1, .hero h2, .hero h3, .hero p {{
        color: #FFFFFF !important;
    }}

    .card {{
        background-color: {card_bg};
        color: {text_color};
        padding: 18px;
        border-radius: 14px;
        border: 1px solid {border_color};
        margin-bottom: 12px;
    }}

    .card h3 {{
        color: {heading_color} !important;
    }}

    .card p {{
        color: {text_color} !important;
    }}

    .stApp input, .stApp textarea,
    .stApp [data-baseweb="select"] > div {{
        color: {text_color} !important;
        background-color: {input_bg} !important;
        border-color: {border_color} !important;
    }}

    .stApp input::placeholder,
    .stApp textarea::placeholder {{
        color: {muted_color} !important;
    }}

    .stButton button,
    .stFormSubmitButton button,
    .stDownloadButton button {{
        background-color: #2E6847 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9px;
        padding: 8px 16px;
    }}

    .stButton button:hover,
    .stFormSubmitButton button:hover,
    .stDownloadButton button:hover {{
        background-color: #244B36 !important;
        color: #FFFFFF !important;
    }}

    [data-testid="stChatMessage"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {text_color} !important;
    }}

    .stApp hr {{
        border-color: {border_color};
    }}

    .stApp a {{
        color: #55A875;
    }}
    </style>
    """, unsafe_allow_html=True)
