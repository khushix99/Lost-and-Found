"""
Views and UI components for the Lost & Found Platform
"""

import streamlit as st
import base64
from datetime import datetime, timedelta
import extra_streamlit_components as stx
from models import CATEGORIES, ITEMS_PER_PAGE, FILTER_TYPES, FILTER_STATUSES, FILTER_CATEGORIES
import utils
import controllers


def render_image(image_obj, **kwargs):
    """Render image from base64 encoded data or show placeholder"""
    if image_obj and isinstance(image_obj, dict) and image_obj.get("data"):
        img_bytes = base64.b64decode(image_obj["data"])
        st.image(img_bytes, **kwargs)
    else:
        st.text("No Image")


def render_navbar(cookie_manager):
    """Render top navigation bar with menu, auth, and theme toggle"""
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
            st.markdown(
                f'<span style="font-size:1.35rem;font-weight:700;color:{brand_color};">🔍 Lost & Found</span>',
                unsafe_allow_html=True
            )

        menu_items = [("Home", "🏠 Home"), ("Post Item", "📝 Post"), ("My Items", "📋 My Items")]
        for i, (key, label) in enumerate(menu_items, start=1):
            with cols[i]:
                is_active = st.session_state["menu"] == key
                btn_type = "primary" if is_active else "secondary"
                st.button(
                    label,
                    key=f"nav_{key}",
                    on_click=controllers.handle_nav_click,
                    args=(key,),
                    use_container_width=True,
                    type=btn_type
                )

        # cols[4] is spacer
        with cols[5]:
            st.button(
                theme_icon,
                key="toggle_theme",
                on_click=controllers.handle_toggle_dark_mode,
                help="Toggle dark/light mode"
            )
        
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
                    controllers.handle_logout(cookie_manager)
    else:
        # Brand | spacer | 🌙 | Sign In | Sign Up
        cols = st.columns([3, 3, 0.5, 1, 1])
        with cols[0]:
            brand_color = "#e0e0ff" if dark else "#1a1a2e"
            st.markdown(
                f'<span style="font-size:1.35rem;font-weight:700;color:{brand_color};">🔍 Lost & Found</span>',
                unsafe_allow_html=True
            )
        # cols[1] is spacer
        with cols[2]:
            st.button(
                theme_icon,
                key="toggle_theme_public",
                on_click=controllers.handle_toggle_dark_mode,
                help="Toggle dark/light mode"
            )
        with cols[3]:
            if st.button("Sign In", key="nav_signin", use_container_width=True):
                st.session_state["show_auth"] = "login"
                st.rerun()
        with cols[4]:
            if st.button("Sign Up", key="nav_signup", use_container_width=True, type="primary"):
                st.session_state["show_auth"] = "register"
                st.rerun()


def render_auth_form(cookie_manager):
    """Render authentication form (login or signup)"""
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
                    controllers.handle_login(username, password, cookie_manager)
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
                    controllers.handle_register(new_user, new_pass, contact)
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


def render_home_page(public=False):
    """Render home page with item listings and filters"""
    st.header("Latest Listings")

    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("Search (Title/Description/Location)")
    with col2:
        filter_type = st.selectbox("Filter by Type", FILTER_TYPES)
    with col3:
        filter_category = st.selectbox("Filter by Category", FILTER_CATEGORIES)

    col4, col5, col6 = st.columns(3)
    with col4:
        filter_status = st.selectbox("Filter by Status", FILTER_STATUSES)
    with col5:
        date_from = st.date_input("From Date", datetime.today() - timedelta(days=90), key="date_from")
    with col6:
        date_to = st.date_input("To Date", datetime.today(), key="date_to")

    items = utils.load_items()
    filtered_items = controllers.filter_items(
        items,
        search_term=search_term,
        filter_type=filter_type,
        filter_status=filter_status,
        filter_category=filter_category,
        date_from=date_from,
        date_to=date_to
    )

    if not filtered_items:
        st.info("No items found.")
    else:
        st.caption(f"Showing {len(filtered_items)} item(s)")

        page_items, total_items, total_pages = controllers.get_paginated_items(
            filtered_items,
            st.session_state["page"]
        )

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
                    st.caption(
                        f"📂 {item.get('category', 'Other')} | Posted by {item['owner']} on {item['date']} | 📍 {item['location']}"
                    )
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


def render_post_item_page():
    """Render post item page"""
    # If redirecting after a successful post, go to Home immediately
    if st.session_state.get("_post_success"):
        st.session_state["_post_success"] = False
        st.session_state["menu"] = "Home"
        st.session_state["page"] = 1
        st.rerun()

    st.header("Post a New Item")

    title = st.text_input("Item Title")
    itype = st.selectbox("Type", CATEGORIES)
    category = st.selectbox("Category", CATEGORIES)
    description = st.text_area("Description")
    location = st.text_input("Location (City, Area, Place)")
    date_str = st.date_input("Date Lost/Found", datetime.today())
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if st.button("Post Item", type="primary"):
        if controllers.handle_post_item(title, itype, category, description, location, date_str, uploaded_file):
            st.session_state["_post_success"] = True
            st.rerun()


def render_my_items_page():
    """Render my items page"""
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
                            controllers.handle_update_item_status(item['id'], 'Resolved')
                    else:
                        if st.button("🔄 Mark as Active", key=f"activate_{item['id']}"):
                            controllers.handle_update_item_status(item['id'], 'Active')
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
                                controllers.handle_delete_item(item['id'])
                        with dc2:
                            if st.button("Cancel", key=f"cancel_del_{item['id']}"):
                                st.session_state[confirm_key] = False
                                st.rerun()
