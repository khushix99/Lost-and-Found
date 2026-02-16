import os
import hashlib
import secrets
import re
import uuid
import base64
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

load_dotenv()  # Load variables from .env file
MONGO_URI = os.getenv("MONGO_URI", "")
_client = None
_db = None

MAX_IMAGE_SIZE = 1 * 1024 * 1024  # 1 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}


def get_db():
    global _client, _db
    if _db is None:
        if not MONGO_URI:
            raise RuntimeError("MONGO_URI environment variable is not set")
        _client = MongoClient(MONGO_URI)
        _db = _client["lostfound"]
        _db.users.create_index("username", unique=True)
        _db.items.create_index("created_at")
        _db.items.create_index("owner")
        # Session tokens: auto-expire after 7 days
        _db.sessions.create_index("token", unique=True)
        _db.sessions.create_index("expires_at", expireAfterSeconds=0)
    return _db


# =============================================
# Password Utilities
# =============================================

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"


def verify_password(password, stored_hash):
    if '$' not in stored_hash:
        return hashlib.sha256(password.encode()).hexdigest() == stored_hash
    salt, _ = stored_hash.split('$', 1)
    return hash_password(password, salt) == stored_hash


# =============================================
# Validation
# =============================================

def validate_registration(username, password, contact_info):
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not contact_info or not contact_info.strip():
        return False, "Contact info is required."
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_pattern = r'^\+?[0-9\s\-]{7,15}$'
    if not (re.match(email_pattern, contact_info) or re.match(phone_pattern, contact_info)):
        return False, "Contact info must be a valid email or phone number."
    return True, ""


# =============================================
# User Operations
# =============================================

def register_user(username, password, contact_info):
    valid, error_msg = validate_registration(username, password, contact_info)
    if not valid:
        return False, error_msg
    db = get_db()
    try:
        db.users.insert_one({
            "username": username,
            "password": hash_password(password),
            "contact_info": contact_info
        })
        return True, "User registered successfully"
    except DuplicateKeyError:
        return False, "Username already exists"


def authenticate_user(username, password):
    db = get_db()
    user = db.users.find_one({"username": username})
    if user is None:
        return False
    stored_hash = user["password"]
    if verify_password(password, stored_hash):
        if '$' not in stored_hash:
            db.users.update_one(
                {"username": username},
                {"$set": {"password": hash_password(password)}}
            )
        return True
    return False


def get_user_contact(username):
    db = get_db()
    user = db.users.find_one({"username": username}, {"contact_info": 1})
    if user:
        return user.get("contact_info", "No contact info")
    return "No contact info"


# =============================================
# Item Operations
# =============================================

def generate_item_id():
    return str(uuid.uuid4())[:8]


def save_item(item):
    db = get_db()
    item["created_at"] = datetime.now(timezone.utc)
    db.items.insert_one(item)


def load_items():
    db = get_db()
    items = list(db.items.find({}, {"_id": 0}).sort("created_at", 1))
    return items


def update_item_status(item_id, new_status):
    db = get_db()
    db.items.update_one({"id": str(item_id)}, {"$set": {"status": new_status}})


def delete_item(item_id):
    db = get_db()
    db.items.delete_one({"id": str(item_id)})


# =============================================
# Image Utilities
# =============================================

def save_uploaded_image(uploaded_file):
    if uploaded_file is None:
        return None

    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    if len(file_bytes) > MAX_IMAGE_SIZE:
        return None

    content_type = uploaded_file.type
    if content_type not in ALLOWED_IMAGE_TYPES:
        return None

    encoded = base64.b64encode(file_bytes).decode("utf-8")
    return {
        "data": encoded,
        "content_type": content_type
    }


# =============================================
# Session Token Management (persist login)
# =============================================

SESSION_DURATION_DAYS = 7


def create_session(username):
    """Create a session token for a user, store in MongoDB, return token string."""
    db = get_db()
    token = secrets.token_hex(32)
    now = datetime.utcnow()
    expires = now + timedelta(days=SESSION_DURATION_DAYS)
    db.sessions.insert_one({
        "token": token,
        "username": username,
        "created_at": now,
        "expires_at": expires,
    })
    return token


def validate_session(token):
    """Check if a session token is valid. Returns username or None."""
    if not token:
        return None
    db = get_db()
    session = db.sessions.find_one({"token": token})
    if session and session.get("expires_at") > datetime.utcnow():
        return session["username"]
    # Expired or not found
    if session:
        db.sessions.delete_one({"token": token})
    return None


def delete_session(token):
    """Remove a session token (logout)."""
    if not token:
        return
    db = get_db()
    db.sessions.delete_one({"token": token})
