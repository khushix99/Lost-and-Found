"""
Main entry point for the Lost & Found Platform Streamlit App
"""

import streamlit as st
import extra_streamlit_components as stx
from models import CATEGORIES
import styles
import views
import controllers


def main():
    """Main application entry point"""
    # Page configuration
    st.set_page_config(
        page_title="Lost & Found Platform",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize cookie manager and session state
    cookie_manager = stx.CookieManager(key="lf_cookies")
    controllers.initialize_session_state()
    
    # Restore login from cookie if available
    controllers.restore_login_from_cookie(cookie_manager)

    # Apply theme styling
    dark_mode = st.session_state["dark_mode"]
    styles.apply_theme(dark_mode)

    # Render navigation bar
    views.render_navbar(cookie_manager)

    # Route to appropriate page
    if st.session_state["user"]:
        # User is logged in
        if st.session_state["menu"] == "Home":
            views.render_home_page(public=False)
        elif st.session_state["menu"] == "Post Item":
            views.render_post_item_page()
        elif st.session_state["menu"] == "My Items":
            views.render_my_items_page()
    else:
        # User is not logged in
        auth_shown = views.render_auth_form(cookie_manager)
        if not auth_shown:
            views.render_home_page(public=True)



if __name__ == "__main__":
    main()

