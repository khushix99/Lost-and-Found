"""
CSS styling and theme configuration for the Lost & Found Platform
"""

import streamlit as st
from models import DARK_MODE_COLORS, LIGHT_MODE_COLORS, PRIMARY_COLOR, PRIMARY_HOVER


def get_colors(dark_mode: bool) -> dict:
    """Get color palette based on dark mode setting"""
    return DARK_MODE_COLORS if dark_mode else LIGHT_MODE_COLORS


def apply_theme(dark_mode: bool) -> None:
    """Apply theme CSS to the Streamlit app"""
    colors = get_colors(dark_mode)
    
    bg_main = colors["bg_main"]
    bg_card = colors["bg_card"]
    text_color = colors["text_color"]
    border_color = colors["border_color"]
    navbar_text = colors["navbar_text"]
    input_bg = colors["input_bg"]
    input_border = colors["input_border"]
    btn_secondary_bg = colors["btn_secondary_bg"]
    btn_secondary_text = colors["btn_secondary_text"]
    btn_secondary_hover = colors["btn_secondary_hover"]
    heading_color = colors["heading_color"]
    caption_color = colors["caption_color"]
    label_color = colors["label_color"]
    
    st.markdown(f"""
<style>
    /* Hide default sidebar */
    [data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    /* Theme background & text */
    .stApp {{ background-color: {bg_main} !important; }}
    .stApp, .stApp p, .stApp span, .stApp div {{ color: {text_color}; }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{ color: {heading_color} !important; }}
    
    /* Captions & muted text */
    [data-testid="stCaptionContainer"], .stCaption {{ color: {caption_color} !important; }}

    /* Input fields */
    [data-testid="stTextInput"] input, 
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stDateInput"] input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {input_border} !important;
    }}
    
    /* Input labels */
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stSelectbox"] label,
    [data-testid="stDateInput"] label,
    [data-testid="stFileUploader"] label {{
        color: {label_color} !important;
        font-weight: 500 !important;
    }}
    
    /* Selectbox dropdown */
    [data-baseweb="select"] {{ background-color: {input_bg} !important; }}
    [data-baseweb="popover"] {{ background-color: {bg_card} !important; }}
    [data-baseweb="menu"] {{ background-color: {bg_card} !important; }}
    [data-baseweb="menu"] li {{ color: {text_color} !important; }}
    [data-baseweb="menu"] li:hover {{ background-color: {border_color} !important; }}

    /* Profile popover — force background on all layers */
    [data-baseweb="popover"] [data-baseweb="popover-inner"] {{
        background-color: {bg_card} !important;
        border-radius: 12px !important;
    }}
    [data-testid="stPopoverBody"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
    }}
    [data-testid="stPopoverBody"] *:not(button) {{
        background-color: {bg_card} !important;
    }}
    [data-testid="stPopoverBody"] p,
    [data-testid="stPopoverBody"] span {{
        color: {text_color} !important;
        background-color: transparent !important;
    }}
    [data-testid="stPopoverBody"] hr {{
        border-color: {border_color} !important;
        background-color: transparent !important;
    }}
    [data-testid="stPopoverBody"] button,
    [data-testid="stPopoverBody"] button * {{
        background-color: {PRIMARY_COLOR} !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
    }}
    [data-testid="stPopoverBody"] .stButton {{
        background-color: transparent !important;
    }}
    .profile-card {{
        text-align: center;
        padding: 0.8rem 1rem;
    }}
    .profile-card .profile-avatar {{
        width: 52px; height: 52px;
        border-radius: 50%;
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #3b82f6 100%);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.4rem;
        color: #fff;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 8px rgba(108,99,255,0.35);
    }}
    .profile-card .profile-name {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {heading_color};
        margin-bottom: 0.3rem;
    }}
    .profile-card .profile-label {{
        font-size: 0.78rem;
        color: {caption_color};
        margin-bottom: 0.6rem;
    }}

    /* Secondary buttons - high visibility */
    [data-testid="baseButton-secondary"],
    button[kind="secondary"],
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {{
        background-color: {btn_secondary_bg} !important;
        color: {btn_secondary_text} !important;
        border: none !important;
        font-weight: 500 !important;
    }}
    [data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {{
        background-color: {btn_secondary_hover} !important;
        color: #ffffff !important;
    }}

    /* Primary buttons keep purple */
    [data-testid="baseButton-primary"] {{
        background-color: {PRIMARY_COLOR} !important;
        color: #ffffff !important;
        border: none !important;
    }}
    [data-testid="baseButton-primary"]:hover {{
        background-color: {PRIMARY_HOVER} !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px;
    }}
    [data-testid="stExpander"] summary {{
        color: {text_color} !important;
        background-color: {bg_card} !important;
    }}
    [data-testid="stExpander"] summary * {{
        color: {text_color} !important;
        background-color: {bg_card} !important;
    }}
    [data-testid="stExpander"] summary:hover {{ color: {PRIMARY_COLOR} !important; }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        background-color: {bg_card} !important;
    }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] *:not(button):not(button *) {{
        background-color: {bg_card} !important;
        color: {text_color} !important;
    }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] p,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] span {{
        background-color: transparent !important;
        color: {text_color} !important;
    }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] strong {{
        color: {heading_color} !important;
        background-color: transparent !important;
    }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] button,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] button * {{
        background-color: {btn_secondary_bg} !important;
        color: {btn_secondary_text} !important;
        border: none !important;
    }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] .stButton {{
        background-color: transparent !important;
    }}

    /* Info/Success/Error boxes */
    [data-testid="stAlert"] {{ background-color: {bg_card} !important; border-color: {border_color} !important; }}

    /* Auth form card */
    .auth-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}

    /* Markdown dividers */
    hr {{ border-color: {border_color} !important; opacity: 0.5; }}

    /* Circular avatar */
    .avatar-circle {{
        width: 38px; height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #3b82f6 100%);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        color: #fff;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(108,99,255,0.35);
        transition: transform 0.15s;
    }}
    .avatar-circle:hover {{ transform: scale(1.08); }}

    /* Card styling */
    .item-card {{
        background: {bg_card};
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border: 1px solid {border_color};
    }}
    [data-testid="stAppViewBlockContainer"] {{ max-width: 1200px; margin: 0 auto; }}

    /* Fix Streamlit button alignment in columns */
    [data-testid="stHorizontalBlock"] {{ align-items: center; }}
    [data-testid="baseButton-secondary"], [data-testid="baseButton-primary"] {{
        padding: 0.4rem 1rem !important;
        font-size: 0.9rem !important;
    }}

    /* File uploader */
    [data-testid="stFileUploader"] {{ 
        background-color: {bg_card} !important; 
        border: 2px dashed {input_border} !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }}
    [data-testid="stFileUploader"] label {{ color: {label_color} !important; font-weight: 500 !important; }}
    [data-testid="stFileUploader"] section {{ 
        background-color: {bg_card} !important; 
        border: none !important;
        color: {text_color} !important;
    }}
    [data-testid="stFileUploader"] section > div {{ color: {text_color} !important; }}
    [data-testid="stFileUploader"] small {{ color: {caption_color} !important; }}
    [data-testid="stFileUploader"] button {{
        background-color: {btn_secondary_bg} !important;
        color: {btn_secondary_text} !important;
        border: none !important;
    }}

    /* ── Responsive ── */
    @media (max-width: 768px) {{
        [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; }}
        [data-testid="stColumn"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
    }}
    @media (min-width: 769px) and (max-width: 1024px) {{
        [data-testid="stColumn"] {{ min-width: 48% !important; }}
    }}
</style>
""", unsafe_allow_html=True)
