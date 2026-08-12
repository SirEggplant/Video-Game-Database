import uuid
import hashlib
import hmac
from passlib.context import CryptContext
from src.db import execute_query

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _find_user(identifier: str, field: str):
    """Return the user record used for authentication, if it exists."""
    return execute_query(
        f'SELECT user_uuid, username, email, password, first_name, last_name '
        f'FROM "user" WHERE {field} = %s',
        (identifier,),
        fetchone=True,
    )

def _migrate_to_bcrypt(user_uuid: str, plain_password: str):
    """Update the user's password to bcrypt hash after a successful login."""
    hashed = password_context.hash(plain_password)
    execute_query(
        'UPDATE "user" SET password = %s WHERE user_uuid = %s',
        (hashed, user_uuid),
    )

def _verify_password(user, password: str) -> bool:
    """
    Verify the provided password against the stored hash.
    Supports bcrypt, legacy SHA‑512 (with and without salt), and plaintext.
    Migrates plaintext/SHA‑512 to bcrypt on success.
    """
    user_uuid, _username, _email, stored_password, *_ = user

    # 1. bcrypt (new users)
    if stored_password.startswith("$2"):
        if password_context.verify(password, stored_password):
            return True
        return False

    # 2. Legacy SHA‑512 (imported from the original school project)
    if len(stored_password) == 128 and all(c in "0123456789abcdef" for c in stored_password.lower()):
        # Standard SHA‑512 of the password
        if hashlib.sha512(password.encode()).hexdigest() == stored_password:
            _migrate_to_bcrypt(user_uuid, password)
            return True
        # SHA‑512 of password + user_uuid (some older versions used this)
        if hashlib.sha512((password + str(user_uuid)).encode()).hexdigest() == stored_password:
            _migrate_to_bcrypt(user_uuid, password)
            return True
        return False

    # 3. Plaintext (imported from your CSV seed)
    if stored_password == password:
        _migrate_to_bcrypt(user_uuid, password)
        return True

    return False

def login_with_user(username: str, password: str):
    user = _find_user(username, "username")
    if not user or not _verify_password(user, password):
        return None
    execute_query('UPDATE "user" SET last_access_date = CURRENT_DATE WHERE username = %s', (username,))
    return user

def login_with_email(email: str, password: str):
    user = _find_user(email, "email")
    if not user or not _verify_password(user, password):
        return None
    execute_query('UPDATE "user" SET last_access_date = CURRENT_DATE WHERE email = %s', (email,))
    return user

def register(username, password, firstname, lastname, email):
    sql_insert = """
        INSERT INTO "user"
        (user_uuid, username, password, first_name, last_name, email, total_playtime, creation_date, last_access_date)
        VALUES (%s, %s, %s, %s, %s, %s, 0, CURRENT_DATE, CURRENT_DATE)
        RETURNING *
    """
    user_id = str(uuid.uuid4())
    hashed = password_context.hash(password)
    try:
        return execute_query(sql_insert, (user_id, username, hashed, firstname, lastname, email), fetchone=True)
    except Exception:
        return None