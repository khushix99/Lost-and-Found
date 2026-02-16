import streamlit as st
import utils
import base64
from datetime import datetime, timedelta
import extra_streamlit_components as stx

ITEMS_PER_PAGE = 10
CATEGORIES = ["Electronics", "Keys", "Wallet/Purse", "Documents", "Clothing", "Bags", "Jewelry", "Pets", "Other"]

st.set_page_config(page_title="Lost & Found Platform", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")

# ── Cookie Manager (persists login across refreshes) ──
cookie_manager = stx.CookieManager(key="lf_cookies")

# ── Session State Init ──
for key, default in [("user", None), ("menu", "Home"), ("page", 1), ("show_auth", None), ("dark_mode", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Restore login from cookie if not already logged in ──
if st.session_state["user"] is None:
    token = cookie_manager.get("session_token")
    if token:
        restored_user = utils.validate_session(token)
        if restored_user:
            st.session_state["user"] = restored_user
        else:
            # Token invalid/expired — clean up cookie
            cookie_manager.delete("session_token")

# ── Theme-aware CSS ──
dark = st.session_state["dark_mode"]

# Dark mode colors
if dark:
    bg_main = "#0e1117"
    bg_card = "#1a1a2e"
    text_color = "#e0e0e0"
    text_muted = "#a0a0a0"
    border_color = "#2d2d44"
    navbar_text = "#e0e0ff"
    input_bg = "#1e1e2e"
    input_border = "#3d3d5c"
    btn_secondary_bg = "#3d3d5c"
    btn_secondary_text = "#ffffff"
    btn_secondary_hover = "#4d4d6c"
    heading_color = "#ffffff"
    caption_color = "#b0b0b0"
    label_color = "#e0e0e0"
# Light mode colors (high contrast)
else:
    bg_main = "#f8f9fa"
    bg_card = "#ffffff"
    text_color = "#212529"
    text_muted = "#6c757d"
    border_color = "#c0c4c8"
    navbar_text = "#1a1a2e"
    input_bg = "#ffffff"
    input_border = "#adb5bd"
    btn_secondary_bg = "#4a6cf7"
    btn_secondary_text = "#ffffff"
    btn_secondary_hover = "#3b5de7"
    heading_color = "#1a1a2e"
    caption_color = "#495057"
    label_color = "#212529"

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
        background-color: #6c63ff !important;
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
        background: linear-gradient(135deg, #6c63ff 0%, #3b82f6 100%);
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
        background-color: #6c63ff !important;
        color: #ffffff !important;
        border: none !important;
    }}
    [data-testid="baseButton-primary"]:hover {{
        background-color: #5a52d5 !important;
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
    [data-testid="stExpander"] summary:hover {{ color: #6c63ff !important; }}
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
        background: linear-gradient(135deg, #6c63ff 0%, #3b82f6 100%);
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


def render_image(image_obj, **kwargs):
    if image_obj and isinstance(image_obj, dict) and image_obj.get("data"):
        img_bytes = base64.b64decode(image_obj["data"])
        st.image(img_bytes, **kwargs)
    else:
        st.text("No Image")


def nav_click(page):
    st.session_state["menu"] = page
    st.session_state["page"] = 1
    st.session_state["show_auth"] = None


def toggle_dark_mode():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]


def render_navbar():
    """Top navigation bar with menu left, auth/profile right, and dark mode toggle."""
    logged_in = st.session_state["user"] is not None
    dark = st.session_state["dark_mode"]
    theme_icon = "☀️" if dark else "🌙"

    if logged_in:
        username = st.session_state["user"]
        initial = username[0].upper()
        # Brand | Home | Post | My Items | spacer | 🌙 | 👤 Profile
        cols = st.columns([2.5, 1, 1, 1, 2, 0.5, 1])
        with cols[0]:
            brand_color = "#e0e0ff" if dark else "#1a1a2e"
            st.markdown(f'<span style="font-size:1.35rem;font-weight:700;color:{brand_color};">🔍 Lost & Found</span>', unsafe_allow_html=True)

        menu_items = [("Home", "🏠 Home"), ("Post Item", "📝 Post"), ("My Items", "📋 My Items")]
        for i, (key, label) in enumerate(menu_items, start=1):
            with cols[i]:
                is_active = st.session_state["menu"] == key
                btn_type = "primary" if is_active else "secondary"
                st.button(label, key=f"nav_{key}", on_click=nav_click, args=(key,), use_container_width=True, type=btn_type)

        # cols[4] is spacer
        with cols[5]:
            st.button(theme_icon, key="toggle_theme", on_click=toggle_dark_mode, help="Toggle dark/light mode")
        with cols[6]:
            with st.popover(f"👤 {initial}"):
                st.markdown(f"""
                <div class="profile-card">
                    <div class="profile-avatar">{initial}</div>
                    <div class="profile-name">{username}</div>
                    <div class="profile-label">Signed in</div>
                </div>
                """, unsafe_allow_html=True)
                st.divider()
                if st.button("🚪 Logout", key="nav_logout", use_container_width=True, type="primary"):
                    token = cookie_manager.get("session_token")
                    utils.delete_session(token)
                    cookie_manager.delete("session_token")
                    st.session_state["user"] = None
                    st.session_state["menu"] = "Home"
                    st.session_state["show_auth"] = None
                    st.rerun()
    else:
        # Brand | spacer | 🌙 | Sign In | Sign Up
        cols = st.columns([3, 3, 0.5, 1, 1])
        with cols[0]:
            brand_color = "#e0e0ff" if dark else "#1a1a2e"
            st.markdown(f'<span style="font-size:1.35rem;font-weight:700;color:{brand_color};">🔍 Lost & Found</span>', unsafe_allow_html=True)
        # cols[1] is spacer
        with cols[2]:
            st.button(theme_icon, key="toggle_theme_public", on_click=toggle_dark_mode, help="Toggle dark/light mode")
        with cols[3]:
            if st.button("Sign In", key="nav_signin", use_container_width=True):
                st.session_state["show_auth"] = "login"
                st.rerun()
        with cols[4]:
            if st.button("Sign Up", key="nav_signup", use_container_width=True, type="primary"):
                st.session_state["show_auth"] = "register"
                st.rerun()


def show_auth_form():
    """Render sign-in or sign-up form centered on the page."""
    mode = st.session_state.get("show_auth")
    if not mode:
        return False

    left_spacer, center, right_spacer = st.columns([1, 1.5, 1])
    with center:
        st.markdown("---")
        if mode == "login":
            st.subheader("🔑 Sign In")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Login", type="primary", use_container_width=True):
                    if utils.authenticate_user(username, password):
                        # Create persistent session token & store in cookie
                        token = utils.create_session(username)
                        cookie_manager.set("session_token", token,
                                           expires_at=datetime.now() + timedelta(days=7))
                        st.session_state["user"] = username
                        st.session_state["menu"] = "Home"
                        st.session_state["show_auth"] = None
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
            with c2:
                if st.button("Cancel", key="cancel_login", use_container_width=True):
                    st.session_state["show_auth"] = None
                    st.rerun()
            st.caption("Don't have an account?")
            if st.button("Create one →", key="switch_register"):
                st.session_state["show_auth"] = "register"
                st.rerun()
            st.markdown("")
            if st.button("🏠 Back to Home", key="home_login", use_container_width=True):
                st.session_state["show_auth"] = None
                st.rerun()
        else:
            st.subheader("📝 Sign Up")
            new_user = st.text_input("Username", key="reg_user")
            new_pass = st.text_input("Password", type="password", key="reg_pass")
            contact = st.text_input("Contact (Email / Phone)", key="reg_contact")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Register", type="primary", use_container_width=True):
                    success, msg = utils.register_user(new_user, new_pass, contact)
                    if success:
                        st.success(msg + " — You can now sign in.")
                        st.session_state["show_auth"] = "login"
                        st.rerun()
                    else:
                        st.error(msg)
            with c2:
                if st.button("Cancel", key="cancel_reg", use_container_width=True):
                    st.session_state["show_auth"] = None
                    st.rerun()
            st.caption("Already have an account?")
            if st.button("Sign in →", key="switch_login"):
                st.session_state["show_auth"] = "login"
                st.rerun()
            st.markdown("")
            if st.button("🏠 Back to Home", key="home_reg", use_container_width=True):
                st.session_state["show_auth"] = None
                st.rerun()
        st.markdown("---")
    return True


def main():
    render_navbar()

    if st.session_state["user"]:
        if st.session_state["menu"] == "Home":
            show_home()
        elif st.session_state["menu"] == "Post Item":
            show_post_item()
        elif st.session_state["menu"] == "My Items":
            show_my_items()
    else:
        # Show auth form if requested, otherwise show public home
        auth_shown = show_auth_form()
        if not auth_shown:
            show_home(public=True)


def show_home(public=False):
    st.header("Latest Listings")

    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("Search (Title/Description/Location)")
    with col2:
        filter_type = st.selectbox("Filter by Type", ["All", "Lost", "Found"])
    with col3:
        filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES)

    col4, col5, col6 = st.columns(3)
    with col4:
        filter_status = st.selectbox("Filter by Status", ["All", "Active", "Resolved"])
    with col5:
        date_from = st.date_input("From Date", datetime.today() - timedelta(days=90), key="date_from")
    with col6:
        date_to = st.date_input("To Date", datetime.today(), key="date_to")

    items = utils.load_items()

    filtered_items = []
    for item in items:
        if filter_type != "All" and item['type'] != filter_type:
            continue
        if filter_status != "All" and item.get('status', 'Active') != filter_status:
            continue
        if filter_category != "All" and item.get('category', 'Other') != filter_category:
            continue
        if search_term:
            term = search_term.lower()
            if (term not in item['title'].lower()
                    and term not in item['description'].lower()
                    and term not in item.get('location', '').lower()):
                continue
        try:
            item_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
            if item_date < date_from or item_date > date_to:
                continue
        except (ValueError, KeyError):
            pass
        filtered_items.append(item)

    filtered_items = list(reversed(filtered_items))
    total_items = len(filtered_items)
    total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

    if not filtered_items:
        st.info("No items found.")
    else:
        st.caption(f"Showing {total_items} item(s)")

        start_idx = (st.session_state["page"] - 1) * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
        page_items = filtered_items[start_idx:end_idx]

        for item in page_items:
            with st.container():
                st.markdown("---")
                c1, c2 = st.columns([1, 3])
                with c1:
                    render_image(item.get("image"), use_container_width=True)
                with c2:
                    st.subheader(item['title'])
                    type_color = "red" if item['type'] == 'Lost' else "green"
                    status_color = "green" if item.get('status') == 'Resolved' else "orange"
                    st.markdown(
                        f"<span style='background:{type_color};color:white;padding:2px 10px;border-radius:12px;font-size:0.85em;'>{item['type']}</span> "
                        f"<span style='background:{status_color};color:white;padding:2px 10px;border-radius:12px;font-size:0.85em;'>{item.get('status', 'Active')}</span>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"📂 {item.get('category', 'Other')} | Posted by {item['owner']} on {item['date']} | 📍 {item['location']}")
                    st.write(item['description'])

                    if not public:
                        if st.button("📞 Contact Owner", key=f"contact_{item['id']}"):
                            contact = utils.get_user_contact(item['owner'])
                            st.success(f"Contact Info: {contact}")
                    else:
                        st.caption("Login to view contact info")

        if total_pages > 1:
            st.markdown("---")
            pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
            with pcol1:
                if st.button("⬅️ Previous", disabled=(st.session_state["page"] <= 1)):
                    st.session_state["page"] -= 1
                    st.rerun()
            with pcol2:
                st.markdown(f"<center>Page {st.session_state['page']} of {total_pages}</center>", unsafe_allow_html=True)
            with pcol3:
                if st.button("Next ➡️", disabled=(st.session_state["page"] >= total_pages)):
                    st.session_state["page"] += 1
                    st.rerun()


def show_post_item():
    # If redirecting after a successful post, go to Home immediately
    if st.session_state.get("_post_success"):
        st.session_state["_post_success"] = False
        st.session_state["menu"] = "Home"
        st.session_state["page"] = 1
        st.rerun()

    st.header("Post a New Item")

    title = st.text_input("Item Title")
    itype = st.selectbox("Type", ["Lost", "Found"])
    category = st.selectbox("Category", CATEGORIES)
    description = st.text_area("Description")
    location = st.text_input("Location (City, Area, Place)")
    date_str = st.date_input("Date Lost/Found", datetime.today())
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if st.button("Post Item", type="primary"):
        if not title or not description or not location:
            st.error("Please fill in all required fields.")
        else:
            image_obj = None
            if uploaded_file:
                image_obj = utils.save_uploaded_image(uploaded_file)
                if image_obj is None:
                    st.error("Image must be JPG/PNG and under 1 MB.")
                    st.stop()

            new_item = {
                "id": utils.generate_item_id(),
                "title": title,
                "type": itype,
                "category": category,
                "description": description,
                "location": location,
                "date": str(date_str),
                "image": image_obj,
                "owner": st.session_state["user"],
                "status": "Active"
            }
            utils.save_item(new_item)
            st.session_state["_post_success"] = True
            st.rerun()


def show_my_items():
    st.header("My Items")
    user = st.session_state["user"]
    items = utils.load_items()

    my_items = [i for i in items if i['owner'] == user]

    if not my_items:
        st.info("You haven't posted any items yet.")
    else:
        for item in my_items:
            type_label = item['type']
            status_label = item.get('status', 'Active')
            with st.expander(f"{item['title']}  —  {type_label}  •  {status_label}"):
                st.write(f"**Category:** {item.get('category', 'Other')}")
                st.write(f"**Description:** {item['description']}")
                st.write(f"**Location:** {item['location']}")
                st.write(f"**Date:** {item['date']}")
                render_image(item.get("image"), width=200)

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if item.get('status', 'Active') == 'Active':
                        if st.button("✅ Mark as Resolved", key=f"resolve_{item['id']}"):
                            utils.update_item_status(item['id'], 'Resolved')
                            st.success("Item marked as resolved!")
                            st.rerun()
                    else:
                        if st.button("🔄 Mark as Active", key=f"activate_{item['id']}"):
                            utils.update_item_status(item['id'], 'Active')
                            st.success("Item marked as active!")
                            st.rerun()
                with bcol2:
                    confirm_key = f"confirm_del_{item['id']}"
                    if confirm_key not in st.session_state:
                        st.session_state[confirm_key] = False

                    if not st.session_state[confirm_key]:
                        if st.button("🗑️ Delete Item", key=f"del_{item['id']}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        st.warning("Are you sure you want to delete this item?")
                        dc1, dc2 = st.columns(2)
                        with dc1:
                            if st.button("Yes, Delete", key=f"yes_del_{item['id']}", type="primary"):
                                utils.delete_item(item['id'])
                                st.session_state[confirm_key] = False
                                st.success("Item deleted!")
                                st.rerun()
                        with dc2:
                            if st.button("Cancel", key=f"cancel_del_{item['id']}"):
                                st.session_state[confirm_key] = False
                                st.rerun()


if __name__ == "__main__":
    main()
