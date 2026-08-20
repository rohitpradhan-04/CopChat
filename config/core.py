import os

from dotenv import load_dotenv

load_dotenv()


class environmentVariables:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./copchat.db")
    
    # SMTP Email Credentials
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USER", "noreply@copchat.com"))
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "CopChat Portal")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "t", "yes")
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "false").lower() in ("true", "1", "t", "yes")

    # JWT & Auth
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "copchat-super-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

