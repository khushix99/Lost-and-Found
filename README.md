# 🔍 Lost & Found Platform

A full-stack web application built with **Python** and **Streamlit** that enables users to post, search, and manage lost and found items. It features secure authentication, persistent login sessions, cloud-based storage via **MongoDB Atlas**, and Base64 image encoding — all wrapped in a responsive, theme-aware UI.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
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
├── app.py              # Main Streamlit application (UI, routing, CSS theming)
├── utils.py            # Backend logic (MongoDB, auth, CRUD, image handling)
├── verify_logic.py     # Test suite for all backend functions
├── requirements.txt    # Python dependencies
├── .env                # MongoDB connection string (not committed)
├── .gitignore          # Ignores .env, .venv, __pycache__
└── README.md           # This file
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
