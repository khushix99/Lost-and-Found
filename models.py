"""
Data models and constants for the Lost & Found Platform
"""

# Configuration
ITEMS_PER_PAGE = 10

CATEGORIES = [
    "Electronics", "Keys", "Wallet/Purse", "Documents", 
    "Clothing", "Bags", "Jewelry", "Pets", "Other"
]

ITEM_TYPES = ["Lost", "Found"]

ITEM_STATUSES = ["Active", "Resolved"]

FILTER_TYPES = ["All", "Lost", "Found"]

FILTER_STATUSES = ["All", "Active", "Resolved"]

FILTER_CATEGORIES = ["All"] + CATEGORIES


# Color Schemes
DARK_MODE_COLORS = {
    "bg_main": "#0e1117",
    "bg_card": "#1a1a2e",
    "text_color": "#e0e0e0",
    "text_muted": "#a0a0a0",
    "border_color": "#2d2d44",
    "navbar_text": "#e0e0ff",
    "input_bg": "#1e1e2e",
    "input_border": "#3d3d5c",
    "btn_secondary_bg": "#3d3d5c",
    "btn_secondary_text": "#ffffff",
    "btn_secondary_hover": "#4d4d6c",
    "heading_color": "#ffffff",
    "caption_color": "#b0b0b0",
    "label_color": "#e0e0e0",
}

LIGHT_MODE_COLORS = {
    "bg_main": "#f8f9fa",
    "bg_card": "#ffffff",
    "text_color": "#212529",
    "text_muted": "#6c757d",
    "border_color": "#c0c4c8",
    "navbar_text": "#1a1a2e",
    "input_bg": "#ffffff",
    "input_border": "#adb5bd",
    "btn_secondary_bg": "#4a6cf7",
    "btn_secondary_text": "#ffffff",
    "btn_secondary_hover": "#3b5de7",
    "heading_color": "#1a1a2e",
    "caption_color": "#495057",
    "label_color": "#212529",
}

# Primary brand color
PRIMARY_COLOR = "#6c63ff"
PRIMARY_HOVER = "#5a52d5"


class Item:
    """Item model"""
    def __init__(self, id, title, itype, category, description, location, date, 
                 image=None, owner=None, status="Active"):
        self.id = id
        self.title = title
        self.type = itype
        self.category = category
        self.description = description
        self.location = location
        self.date = date
        self.image = image
        self.owner = owner
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "category": self.category,
            "description": self.description,
            "location": self.location,
            "date": self.date,
            "image": self.image,
            "owner": self.owner,
            "status": self.status,
        }

    @staticmethod
    def from_dict(data):
        return Item(
            id=data.get("id"),
            title=data.get("title"),
            itype=data.get("type"),
            category=data.get("category"),
            description=data.get("description"),
            location=data.get("location"),
            date=data.get("date"),
            image=data.get("image"),
            owner=data.get("owner"),
            status=data.get("status", "Active"),
        )


class User:
    """User model"""
    def __init__(self, username, password_hash=None, contact=None):
        self.username = username
        self.password_hash = password_hash
        self.contact = contact

    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "contact": self.contact,
        }

    @staticmethod
    def from_dict(data):
        return User(
            username=data.get("username"),
            password_hash=data.get("password_hash"),
            contact=data.get("contact"),
        )
