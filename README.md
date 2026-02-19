# 🔍 Lost & Found Platform

A full-stack web application built with **Python** and **Streamlit** that enables users to post, search, and manage lost and found items. It features secure authentication, persistent login sessions, cloud-based storage via **MongoDB Atlas**, and Base64 image encoding — all wrapped in a responsive, theme-aware UI.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Architecture & Modules](#-architecture--modules)
- [How It Works](#-how-it-works)
  - [Authentication & Session Management](#1-authentication--session-management)
  - [Posting Items](#2-posting-items)
  - [Image Storage (Base64 in MongoDB)](#3-image-storage-base64-in-mongodb)
  - [Browsing & Filtering](#4-browsing--filtering)
  - [Managing Your Items](#5-managing-your-items)
- [Database Schema](#-database-schema)
- [Setup & Installation](#-setup--installation)
- [Environment Variables](#-environment-variables)
- [Running the App](#-running-the-app)
- [Running Tests](#-running-tests)

---

## ✨ Features

| Feature | Description |
|---|---|
| **User Authentication** | Sign up / Sign in with PBKDF2-HMAC-SHA256 hashed passwords |
| **Persistent Login** | Cookie-based session tokens survive browser refreshes (7-day expiry) |
| **Post Items** | Report lost or found items with title, description, category, location, date, and image |
| **Image Upload** | JPG/PNG images (max 1 MB) stored as Base64 strings directly in MongoDB |
| **Search & Filter** | Filter by type (Lost/Found), category, status, date range, and free-text search |
| **Pagination** | 10 items per page with Previous/Next navigation |
| **Item Management** | Mark items as Resolved/Active, delete with confirmation |
| **Contact Owner** | Logged-in users can view the poster's contact info |
| **Dark/Light Mode** | Toggle theme with full CSS theming across all components |
| **Responsive Design** | Mobile-friendly layout with CSS media queries |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (Python), Custom CSS |
| **Backend** | Python 3.11+ |
| **Database** | MongoDB Atlas (cloud) |
| **Auth** | PBKDF2-HMAC-SHA256 + session tokens + browser cookies |
| **Image Storage** | Base64 encoding stored in MongoDB documents |
| **Session Persistence** | `extra-streamlit-components` CookieManager |
| **Environment** | `python-dotenv` for secure config |

---

## 📁 Project Structure

```
Lost-and-Found/
├── app.py                 # Main Streamlit entry point - minimal & clean
├── models.py              # Data models and constants
├── views.py               # UI components and rendering
├── controllers.py         # Business logic and handlers
├── styles.py              # CSS theming and styling
├── utils.py               # MongoDB operations and utilities
├── verify_logic.py        # Test suite for backend functions
├── requirements.txt       # Python dependencies
├── .env                   # MongoDB connection string (not committed)
├── .gitignore             # Ignores .env, .venv, __pycache__
└── README.md              # This file
```

---

## 🏗 Architecture & Modules

This project follows a **Model-View-Controller (MVC) pattern** for clean separation of concerns:

### **1. `app.py` — Main Application Entry Point**
- **Responsibility:** Initialize Streamlit, orchestrate routing, coordinate modules
- **Lines of Code:** ~57 (lean & maintainable)
- **Key Functions:**
  - `main()` — Initialize config, load theme, route to pages
  
**Example:**
```python
def main():
    st.set_page_config(...)
    cookie_manager = stx.CookieManager(key="lf_cookies")
    controllers.initialize_session_state()
    styles.apply_theme(st.session_state["dark_mode"])
    views.render_navbar(cookie_manager)
    
    # Route to correct page based on session state
    if st.session_state["user"]:
        if st.session_state["menu"] == "Home":
            views.render_home_page(public=False)
        # ... other routes
```

---

### **2. `models.py` — Data Models & Constants**
- **Responsibility:** Define data structures and application constants
- **Key Classes:**
  - `Item` — Represents a lost/found item with validation and serialization
  - `User` — Represents a user account
  
- **Key Constants:**
  - `CATEGORIES` — List of item categories
  - `ITEMS_PER_PAGE` — Pagination size (10)
  - `DARK_MODE_COLORS` / `LIGHT_MODE_COLORS` — Theme color palettes

**Example:**
```python
class Item:
    def __init__(self, id, title, itype, category, ...):
        self.id = id
        self.title = title
        # ... other fields
    
    def to_dict(self):
        """Convert to MongoDB-compatible dictionary"""
        return {...}
```

---

### **3. `views.py` — UI Components & Rendering**
- **Responsibility:** All Streamlit UI rendering functions
- **No Business Logic** — Only calls controllers/utils
- **Key Functions:**
  - `render_navbar(cookie_manager)` — Top navigation + theme toggle
  - `render_auth_form(cookie_manager)` — Login/signup forms
  - `render_home_page(public=False)` — Item listings with filters + pagination
  - `render_post_item_page()` — Post new item form
  - `render_my_items_page()` — Manage user's items (edit status, delete)
  - `render_image(image_obj, **kwargs)` — Display Base64-encoded images

**Example:**
```python
def render_home_page(public=False):
    st.header("Latest Listings")
    
    # Filters
    search_term = st.text_input("Search ...")
    filter_type = st.selectbox("Filter by Type", FILTER_TYPES)
    # ... more filters
    
    # Get data via controller
    items = utils.load_items()
    filtered = controllers.filter_items(items, search_term, ...)
    
    # Display
    for item in filtered:
        render_item_card(item)
```

---

### **4. `controllers.py` — Business Logic & Handlers**
- **Responsibility:** Process user actions and orchestrate data flow
- **No Streamlit Calls** — Only receives/returns data
- **Key Functions:**
  - Session Management:
    - `initialize_session_state()` — Setup Streamlit session variables
    - `restore_login_from_cookie(cookie_manager)` — Persist login
    - `handle_logout(cookie_manager)` — Clear session
  
  - Authentication:
    - `handle_login(username, password, cookie_manager)` — Validate and create session
    - `handle_register(username, password, contact)` — New user registration
  
  - Item Operations:
    - `filter_items(items, search_term, ...)` — Apply all filters
    - `get_paginated_items(items, page)` — Handle pagination
    - `handle_post_item(...)` — Validate and save new item
    - `handle_update_item_status(item_id, new_status)` — Mark item resolved/active
    - `handle_delete_item(item_id)` — Delete with cleanup
  
  - Navigation:
    - `handle_nav_click(page)` — Route to menu page
    - `handle_toggle_dark_mode()` — Switch theme

**Example:**
```python
def filter_items(items, search_term="", filter_type="All", ...):
    """Pure function - no Streamlit dependency"""
    filtered = []
    for item in items:
        if filter_type != "All" and item['type'] != filter_type:
            continue
        # ... apply all filters
        filtered.append(item)
    return list(reversed(filtered))  # Newest first
```

---

### **5. `styles.py` — CSS Theming**
- **Responsibility:** Apply dynamic theme styling
- **Key Functions:**
  - `get_colors(dark_mode: bool)` — Return color palette for theme
  - `apply_theme(dark_mode: bool)` — Render all CSS to Streamlit
  
- **Features:**
  - Dark mode: Dim background, light text
  - Light mode: Bright background, dark text
  - Dynamic color application to all components
  - Responsive design (mobile, tablet, desktop)

**Example:**
```python
def apply_theme(dark_mode: bool) -> None:
    colors = get_colors(dark_mode)
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {colors['bg_main']} !important; }}
        [data-testid="stTextInput"] input {{
            background-color: {colors['input_bg']} !important;
            color: {colors['text_color']} !important;
        }}
        /* ... 500+ lines of comprehensive CSS ... */
    </style>
    """, unsafe_allow_html=True)
```

---

### **6. `utils.py` — Database & Utility Functions**
- **Responsibility:** MongoDB operations and helper functions
- **Key Functions:**
  - **User Management:**
    - `register_user(username, password, contact)` — Database insert
    - `authenticate_user(username, password)` — Verify credentials
    - `create_session(username)` — Generate token
    - `validate_session(token)` — Check expiry
    - `delete_session(token)` — Logout cleanup
    - `get_user_contact(username)` — Retrieve contact info
  
  - **Item Operations:**
    - `load_items()` — Get all items from MongoDB
    - `save_item(item_dict)` — Insert new item
    - `update_item_status(item_id, status)` — Mark resolved/active
    - `delete_item(item_id)` — Remove from database
    - `generate_item_id()` — Create unique ID (UUID first 8 chars)
  
  - **Image Handling:**
    - `save_uploaded_image(uploaded_file)` — Base64 encode and validate
    - Validates file type (JPG/PNG) and size (max 1 MB)

---

### **7. `verify_logic.py` — Test Suite**
- **Responsibility:** Automated testing of backend functions
- **Test Database:** `lostfound_test` (separate from production)
- **Coverage:**
  - User registration, authentication, session management
  - Item CRUD operations
  - Image upload validation
  - Input validation edge cases
  - Data consistency checks

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser/User                          │
└──────────────────┬──────────────────────────────────────────┘
                   │ (Streamlit interaction)
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                      views.py (UI)                           │
│  • render_home_page()                                        │
│  • render_post_item_page()                                   │
│  • render_auth_form()                                        │
└──────────────────┬──────────────────────────────────────────┘
                   │ (calls business logic)
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                 controllers.py (Logic)                       │
│  • filter_items()                                            │
│  • handle_post_item()                                        │
│  • handle_login()                                            │
└──────────────────┬──────────────────────────────────────────┘
                   │ (calls database)
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                  utils.py (Database)                         │
│  • load_items()           →────┐                             │
│  • save_item()                 │                             │
│  • authenticate_user()    →────┤                             │
└──────────────────────────┬─────┼──────────────────────────────┘
                           ↓     ↑
                    ┌──────────────────────┐
                    │  MongoDB Atlas       │
                    │  (lostfound DB)      │
                    │  • users collection  │
                    │  • items collection  │
                    │  • sessions coll.    │
                    └──────────────────────┘
```

---

## 🔧 How It Works

### 1. Authentication & Session Management

**Registration:**
1. User submits username, password, and contact info (email or phone).
2. Input is validated: username ≥ 3 chars (alphanumeric + underscore), password ≥ 6 chars, valid email/phone.
3. Password is hashed using **PBKDF2-HMAC-SHA256** with a random 16-byte salt and 100,000 iterations.
4. Stored in MongoDB as: `salt$hash_hex` (e.g., `a1b2c3...$4d5e6f...`).

**Login:**
1. User enters credentials → password is hashed with the stored salt → compared to stored hash.
2. On success, a **64-character session token** (`secrets.token_hex(32)`) is generated.
3. The token is saved in:
   - **MongoDB `sessions` collection** — with username, creation time, and 7-day expiry.
   - **Browser cookie** (`session_token`) — via `extra-streamlit-components` CookieManager.

**Session Persistence (surviving refresh):**
1. On every page load, the app checks `st.session_state["user"]`.
2. If `None`, it reads the `session_token` cookie from the browser.
3. The token is validated against MongoDB's `sessions` collection.
4. If valid and not expired → user is automatically logged back in.
5. If expired → token is deleted from both MongoDB and the browser cookie.

**Logout:**
1. Session token is deleted from MongoDB.
2. Cookie is cleared from the browser.
3. Session state is reset.

**MongoDB TTL Index:**
The `sessions` collection has a TTL index on `expires_at` with `expireAfterSeconds=0`, meaning MongoDB automatically deletes expired sessions — no manual cleanup needed.

---

### 2. Posting Items

When a user posts a lost or found item, the following data is captured:

| Field | Type | Description |
|---|---|---|
| `id` | `string` | UUID-based 8-character unique ID (`uuid4()[:8]`) |
| `title` | `string` | Item title (required) |
| `type` | `string` | "Lost" or "Found" |
| `category` | `string` | One of: Electronics, Keys, Wallet/Purse, Documents, Clothing, Bags, Jewelry, Pets, Other |
| `description` | `string` | Detailed description (required) |
| `location` | `string` | City, area, place (required) |
| `date` | `string` | Date lost/found (YYYY-MM-DD format) |
| `image` | `object/null` | Base64-encoded image (see below) |
| `owner` | `string` | Username of the poster |
| `status` | `string` | "Active" or "Resolved" |
| `created_at` | `datetime` | UTC timestamp for sorting |

After successful posting, the user is automatically redirected to the Home page via a session state flag (`_post_success`).

---

### 3. Image Storage (Base64 in MongoDB)

This project stores images **directly inside MongoDB documents** using Base64 encoding — no separate file server or cloud storage needed.

**Upload Flow:**

```
User selects image file
        ↓
┌─────────────────────────────┐
│  Validation                 │
│  • File type: JPG/PNG only  │
│  • Max size: 1 MB           │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  Read raw bytes             │
│  file_bytes = file.read()   │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  Base64 Encode              │
│  base64.b64encode(bytes)    │
│  → ASCII string             │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  Store in MongoDB           │
│  {                          │
│    "data": "iVBORw0KGg...", │
│    "content_type": "image/  │
│                    jpeg"    │
│  }                          │
└─────────────────────────────┘
```

**How it's stored in the database:**

Each item document in MongoDB contains an `image` field that is either `null` (no image) or an object:

```json
{
  "id": "a1b2c3d4",
  "title": "Lost Phone",
  "type": "Lost",
  "image": {
    "data": "iVBORw0KGgoAAAANSUhEUgAA...",   // Base64-encoded string
    "content_type": "image/jpeg"                // MIME type
  },
  "owner": "john",
  "status": "Active"
}
```

**Display Flow:**

```
Read item from MongoDB
        ↓
Extract image["data"] (Base64 string)
        ↓
base64.b64decode(data) → raw bytes
        ↓
st.image(bytes) → rendered in browser
```

**Why Base64 in MongoDB?**
- **Simplicity** — No separate file storage service needed.
- **Atomic** — Item and its image are always together in one document.
- **Portable** — The entire database is self-contained.
- **Trade-off** — Base64 increases data size by ~33%, but with a 1 MB limit per image this is manageable. MongoDB's 16 MB document limit is never reached.

---

### 4. Browsing & Filtering

The home page displays all items (newest first) with these filters:

| Filter | Options |
|---|---|
| **Search** | Free-text search across title, description, and location |
| **Type** | All / Lost / Found |
| **Category** | All / Electronics / Keys / Wallet/Purse / Documents / Clothing / Bags / Jewelry / Pets / Other |
| **Status** | All / Active / Resolved |
| **Date Range** | From date → To date (default: last 90 days) |

Results are paginated at 10 items per page. Public (logged-out) users can browse but cannot view contact info.

---

### 5. Managing Your Items

The "My Items" page shows only items posted by the logged-in user, displayed in expandable cards. Each card provides:

- **Mark as Resolved** — Toggles status to "Resolved" (or back to "Active")
- **Delete Item** — Two-step confirmation: click Delete → confirm "Yes, Delete" or Cancel
- Full item details: category, description, location, date, and image

---

## 🗄 Database Schema

**Database:** `lostfound` (MongoDB Atlas)

### `users` Collection
```json
{
  "username": "john_doe",           // Unique index
  "password": "a1b2c3...$4d5e6f...", // salt$pbkdf2_hash
  "contact_info": "john@email.com"
}
```

### `items` Collection
```json
{
  "id": "a1b2c3d4",                // 8-char UUID
  "title": "Lost Phone",
  "type": "Lost",                   // "Lost" | "Found"
  "category": "Electronics",
  "description": "Black iPhone 15...",
  "location": "Central Park, NYC",
  "date": "2026-02-15",
  "image": {                        // null if no image
    "data": "iVBORw0KGg...",        // Base64 string
    "content_type": "image/jpeg"
  },
  "owner": "john_doe",
  "status": "Active",              // "Active" | "Resolved"
  "created_at": "2026-02-15T10:30:00Z"
}
```

### `sessions` Collection
```json
{
  "token": "a1b2c3d4e5f6...",      // 64-char hex token (unique index)
  "username": "john_doe",
  "created_at": "2026-02-15T10:30:00Z",
  "expires_at": "2026-02-22T10:30:00Z"  // TTL index — auto-deleted by MongoDB
}
```

**Indexes:**
| Collection | Index | Type |
|---|---|---|
| `users` | `username` | Unique |
| `items` | `created_at` | Regular (sorting) |
| `items` | `owner` | Regular (filtering) |
| `sessions` | `token` | Unique |
| `sessions` | `expires_at` | TTL (auto-delete) |

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11+
- A MongoDB Atlas account (free tier works)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Lost-and-Found.git
cd Lost-and-Found

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
```

This connection string is loaded by `python-dotenv` at startup. The database `lostfound` and all collections/indexes are created automatically on first run.

> ⚠️ Never commit the `.env` file. It is already listed in `.gitignore`.

---

## ▶️ Running the App

```bash
# Make sure virtual environment is activated, then:
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🧪 Running Tests

```bash
python verify_logic.py
```

This runs a comprehensive test suite that:
1. Connects to MongoDB using a separate `lostfound_test` database
2. Tests user registration, duplicate detection, authentication
3. Tests item CRUD operations (create, read, update, delete)
4. Tests image upload validation
5. Tests input validation edge cases
6. Cleans up (drops the test database) after completion

---

## 📄 License

This project was developed as part of an internship to demonstrate practical implementation of web application development concepts including session management, CRUD operations, cloud database integration, and modular code design.
