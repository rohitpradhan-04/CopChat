import secrets
import string
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from config.core import environmentVariables

config = environmentVariables()


def generate_temp_password(length: int = 12) -> str:
    """Generate a secure, random temporary password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    # Ensure at least one uppercase, lowercase, digit, and special char
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*"),
    ]
    password += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    pwd_bytes = password.encode("utf-8")
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:  # noqa: BLE001
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=config.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(
        to_encode,
        config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            config.jwt_secret_key,
            algorithms=[config.jwt_algorithm],
        )
        return payload
    except jwt.PyJWTError:
        return None
