"""
Controllers and business logic for the Lost & Found Platform
"""

import streamlit as st
import utils
from datetime import datetime, timedelta
from models import CATEGORIES, ITEMS_PER_PAGE, FILTER_TYPES, FILTER_STATUSES, FILTER_CATEGORIES
import extra_streamlit_components as stx


def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        "user": None,
        "menu": "Home",
        "page": 1,
        "show_auth": None,
        "dark_mode": False,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def restore_login_from_cookie(cookie_manager):
    """Restore user login from persistent cookie"""
    if st.session_state["user"] is None:
        token = cookie_manager.get("session_token")
        if token:
            restored_user = utils.validate_session(token)
            if restored_user:
                st.session_state["user"] = restored_user
            else:
                # Token invalid/expired — clean up cookie
                cookie_manager.delete("session_token")


def handle_nav_click(page: str):
    """Handle navigation menu click"""
    st.session_state["menu"] = page
    st.session_state["page"] = 1
    st.session_state["show_auth"] = None


def handle_toggle_dark_mode():
    """Toggle dark/light mode"""
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]


def handle_logout(cookie_manager):
    """Handle user logout"""
    token = cookie_manager.get("session_token")
    utils.delete_session(token)
    try:
        cookie_manager.delete("session_token")
    except KeyError:
        pass
    st.session_state["user"] = None
    st.session_state["menu"] = "Home"
    st.session_state["show_auth"] = None
    st.rerun()


def handle_login(username: str, password: str, cookie_manager):
    """Handle user login"""
    if utils.authenticate_user(username, password):
        token = utils.create_session(username)
        cookie_manager.set(
            "session_token",
            token,
            expires_at=datetime.now() + timedelta(days=7)
        )
        st.session_state["user"] = username
        st.session_state["menu"] = "Home"
        st.session_state["show_auth"] = None
        st.rerun()
    else:
        st.error("Invalid username or password")


def handle_register(username: str, password: str, contact: str):
    """Handle user registration"""
    success, msg = utils.register_user(username, password, contact)
    if success:
        st.success(msg + " — You can now sign in.")
        st.session_state["show_auth"] = "login"
        st.rerun()
    else:
        st.error(msg)


def filter_items(items: list, search_term: str = "", filter_type: str = "All",
                filter_status: str = "All", filter_category: str = "All",
                date_from = None, date_to = None) -> list:
    """Apply filters to items list"""
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
            if date_from and date_to:
                item_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
                if item_date < date_from or item_date > date_to:
                    continue
        except (ValueError, KeyError):
            pass
        
        filtered_items.append(item)
    
    return list(reversed(filtered_items))


def get_paginated_items(items: list, page: int, items_per_page: int = ITEMS_PER_PAGE) -> tuple:
    """Get paginated items and page info"""
    total_items = len(items)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    page_items = items[start_idx:end_idx]
    
    return page_items, total_items, total_pages


def handle_post_item(title: str, itype: str, category: str, description: str,
                     location: str, date_obj, uploaded_file) -> bool:
    """Handle posting a new item"""
    if not title or not description or not location:
        st.error("Please fill in all required fields.")
        return False
    
    image_obj = None
    if uploaded_file:
        image_obj = utils.save_uploaded_image(uploaded_file)
        if image_obj is None:
            st.error("Image must be JPG/PNG and under 1 MB.")
            return False
    
    new_item = {
        "id": utils.generate_item_id(),
        "title": title,
        "type": itype,
        "category": category,
        "description": description,
        "location": location,
        "date": str(date_obj),
        "image": image_obj,
        "owner": st.session_state["user"],
        "status": "Active"
    }
    utils.save_item(new_item)
    return True


def handle_update_item_status(item_id: str, new_status: str):
    """Handle updating item status"""
    utils.update_item_status(item_id, new_status)
    st.rerun()


def handle_delete_item(item_id: str):
    """Handle deleting an item"""
    utils.delete_item(item_id)
    st.rerun()
