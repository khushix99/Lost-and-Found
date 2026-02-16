import utils
import os
import io
import base64
import hashlib

# =============================================
# Setup: Point utils at a test database
# =============================================
print("Setting up test environment...")
TEST_DB_NAME = "lostfound_test"

# Override the get_db function to use a test database
_original_get_db = utils.get_db
def _test_get_db():
    db = _original_get_db()
    return db.client[TEST_DB_NAME]

utils.get_db = _test_get_db

# Clean test database
db = utils.get_db()
db.users.drop()
db.items.drop()
db.users.create_index("username", unique=True)
db.items.create_index("created_at")
db.items.create_index("owner")
print("  ✓ Test environment ready.")

# =============================================
# 1. Test Input Validation
# =============================================
print("Testing input validation...")
valid, msg = utils.validate_registration("ab", "password123", "test@example.com")
assert valid == False, "Username too short should fail"

valid, msg = utils.validate_registration("user!@#", "password123", "test@example.com")
assert valid == False, "Invalid username chars should fail"

valid, msg = utils.validate_registration("testuser", "123", "test@example.com")
assert valid == False, "Short password should fail"

valid, msg = utils.validate_registration("testuser", "password123", "")
assert valid == False, "Empty contact should fail"

valid, msg = utils.validate_registration("testuser", "password123", "not-valid")
assert valid == False, "Invalid contact format should fail"

valid, msg = utils.validate_registration("testuser", "password123", "test@example.com")
assert valid == True, "Valid inputs should pass"

valid, msg = utils.validate_registration("testuser", "password123", "+1234567890")
assert valid == True, "Valid phone should pass"
print("  ✓ Input validation passed.")

# =============================================
# 2. Test Registration
# =============================================
print("Testing registration...")
success, msg = utils.register_user("testuser", "password123", "test@example.com")
assert success == True
success, msg = utils.register_user("testuser", "password123", "other@example.com")
assert success == False  # Duplicate user

success, msg = utils.register_user("ab", "password123", "test@example.com")
assert success == False  # Username too short
print("  ✓ Registration passed.")

# =============================================
# 3. Test Authentication (PBKDF2)
# =============================================
print("Testing authentication...")
assert utils.authenticate_user("testuser", "password123") == True
assert utils.authenticate_user("testuser", "wrongpassword") == False
assert utils.authenticate_user("nonexistent", "password123") == False

user_doc = db.users.find_one({"username": "testuser"})
assert "$" in user_doc["password"], "Password should be in PBKDF2 salt$hash format"
print("  ✓ Authentication passed.")

# =============================================
# 4. Test Password Hashing
# =============================================
print("Testing password hashing...")
hash1 = utils.hash_password("mypassword")
hash2 = utils.hash_password("mypassword")
assert hash1 != hash2, "Same password should produce different hashes (different salts)"
assert utils.verify_password("mypassword", hash1) == True
assert utils.verify_password("wrongpassword", hash1) == False

legacy_hash = hashlib.sha256("legacypass".encode()).hexdigest()
assert utils.verify_password("legacypass", legacy_hash) == True
assert utils.verify_password("wrongpass", legacy_hash) == False
print("  ✓ Password hashing passed.")

# =============================================
# 5. Test Item Handling with UUID IDs
# =============================================
print("Testing item handling...")
items = utils.load_items()
assert len(items) == 0

item_id = utils.generate_item_id()
assert isinstance(item_id, str) and len(item_id) == 8, "ID should be 8-char string"

new_item = {
    "id": item_id,
    "title": "Lost Keys",
    "type": "Lost",
    "category": "Keys",
    "description": "Keys with a blue keychain",
    "location": "Park",
    "date": "2023-10-27",
    "image": None,
    "owner": "testuser",
    "status": "Active"
}
utils.save_item(new_item)
loaded_items = utils.load_items()
assert len(loaded_items) == 1
assert loaded_items[0]["title"] == "Lost Keys"
assert loaded_items[0]["category"] == "Keys"

id2 = utils.generate_item_id()
assert id2 != item_id, "IDs should be unique"
print("  ✓ Item handling passed.")

# =============================================
# 6. Test Item Status Update (Mark as Resolved)
# =============================================
print("Testing item status update...")
utils.update_item_status(item_id, "Resolved")
loaded_items = utils.load_items()
assert loaded_items[0]["status"] == "Resolved"

utils.update_item_status(item_id, "Active")
loaded_items = utils.load_items()
assert loaded_items[0]["status"] == "Active"
print("  ✓ Item status update passed.")

# =============================================
# 7. Test Image Save (base64)
# =============================================
print("Testing image save (base64)...")
fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
mock_file = io.BytesIO(fake_png)
mock_file.name = "test_image.png"
mock_file.type = "image/png"
image_obj = utils.save_uploaded_image(mock_file)
assert image_obj is not None
assert isinstance(image_obj, dict)
assert "data" in image_obj
assert "content_type" in image_obj
assert image_obj["content_type"] == "image/png"

decoded = base64.b64decode(image_obj["data"])
assert decoded == fake_png, "Decoded image should match original bytes"

# Reject oversized file
big_file = io.BytesIO(b"\x00" * (2 * 1024 * 1024))
big_file.name = "big.png"
big_file.type = "image/png"
assert utils.save_uploaded_image(big_file) is None, "Should reject files > 1 MB"

# Reject invalid type
bad_file = io.BytesIO(b"data")
bad_file.name = "test.gif"
bad_file.type = "image/gif"
assert utils.save_uploaded_image(bad_file) is None, "Should reject non-jpg/png"
print("  ✓ Image save passed.")

# =============================================
# 8. Test Item with Image + Deletion
# =============================================
print("Testing item deletion...")
item_with_image_id = utils.generate_item_id()
utils.save_item({
    "id": item_with_image_id,
    "title": "Found Phone",
    "type": "Found",
    "category": "Electronics",
    "description": "iPhone found at library",
    "location": "Library",
    "date": "2023-11-01",
    "image": image_obj,
    "owner": "testuser",
    "status": "Active"
})
assert len(utils.load_items()) == 2

utils.delete_item(item_with_image_id)
remaining = utils.load_items()
assert len(remaining) == 1
print("  ✓ Item deletion passed.")

# =============================================
# 9. Test MongoDB Collections
# =============================================
print("Testing MongoDB collections...")
assert db.users.count_documents({}) >= 1
assert db.items.count_documents({}) >= 1

indexes = db.users.index_information()
has_username_index = any("username" in str(v.get("key", "")) for v in indexes.values())
assert has_username_index, "users collection should have username index"
print("  ✓ MongoDB collections passed.")

# =============================================
# 10. Test get_user_contact
# =============================================
print("Testing get_user_contact...")
utils.register_user("contactuser", "pass123456", "hello@world.com")
contact = utils.get_user_contact("contactuser")
assert contact == "hello@world.com"
contact = utils.get_user_contact("nonexistent")
assert contact == "No contact info"
print("  ✓ get_user_contact passed.")

# =============================================
# Cleanup: Drop test database
# =============================================
db.client.drop_database(TEST_DB_NAME)
print("\n=============================")
print("  ALL TESTS PASSED! ✅")
print("=============================")
