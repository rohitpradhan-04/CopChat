# CopChat 🛡️

**CopChat** is a secure real-time messaging and collaboration platform specifically tailored for law enforcement officers (cops). Designed for high confidentiality, departmental hierarchy, and rapid communication across operational units.

---

## 📌 Project Status & Features

### ✅ Completed Features
- **User Registration**: Comprehensive police officer profile onboarding including:
  - Service ID (unique identifier)
  - Rank (Constable, ASI, SI, Inspector, DSP, SP, CP, etc.)
  - Department (Law & Order, Traffic, Crime Branch, Cyber Crime, Special Branch, ATS, etc.)
  - Date of Joining
  - Mobile Number & Email
  - Blood Group & Emergency Contact information
  - Password hashing & secure storage
- **Login**: Secure JWT authentication with first-login password setup
- **Forgot / Reset Password**: Request a short-lived reset token by email or Service ID, then set a new permanent password

### ⏳ Pending Features (To-Do List)
- 🚪 **Logout**: Session termination & token revocation
- 👥 **User Lists**: Directory search and filter officers by rank, department, or location
- 💬 **User Chat**: Encrypted 1-on-1 direct messaging
- 👨‍👩‍👧‍👦 **Groups**: Tactical group creation, broadcast channels, and department-wise group chats
- 📱 **OTP Verification**: Multi-factor authentication via SMS/Email OTP

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM / Database**: [SQLModel](https://sqlmodel.tiangolo.com/) & [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: PostgreSQL
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (Fast Python package installer & resolver)

---

## 🚀 Setup & Installation Guidance

### Prerequisites
- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) installed on your machine:
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- PostgreSQL instance up and running.

---

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/CopChat.git
cd CopChat
```

### 2. Create & Activate Environment using `uv`
```bash
# Create virtual environment
uv venv

# Activate virtual environment
# macOS / Linux:
source .venv/bin/activate

# Windows (Command Prompt):
.venv\Scripts\activate.bat

# Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
uv sync
```

---

### 4. Configure Environment Variables
Copy `.env.example` to create `.env`:
```bash
cp .env.example .env
```

Open `.env` and set your PostgreSQL database credentials:
```env
DATABASE_URL="postgresql://{username}:{password}@{host}:{port}/{database}"
```

*Example:*
```env
DATABASE_URL="postgresql://postgres:password123@localhost:5432/copchat_db"
```

---

### 5. Run Database Migrations
Apply Alembic database migrations to create the required tables:
```bash
uv run alembic upgrade head
```

---

### 6. Run the Application
Start the FastAPI development server:
```bash
uv run uvicorn core.main:app --reload
```

The API will be available at:
- **Server**: `http://127.0.0.1:8000`
- **Interactive API Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 🔐 Forgot Password Flow

1. **Request reset** — `POST /v1/forgot-password` with `email_or_service_id`.
   - Always returns a generic success message (no account enumeration).
   - If an active account matches, a short-lived reset token is emailed in the background.
2. **Reset password** — `POST /v1/reset-password` with `reset_token` and `new_password`.
3. **Login** — use `POST /v1/login` with the new password.

Token lifetime is controlled by `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` (default: `30`).

---

## 📂 Project Structure

```
CopChat/
├── alembic/                # Alembic database migration scripts
├── alembic.ini             # Alembic configuration
├── config/                 # App configuration files
├── core/                   # Core application package
│   ├── database.py         # Database connection & session setup
│   ├── main.py             # FastAPI entrypoint
│   ├── models/             # Database models (User, Rank, Department, etc.)
│   └── routers/            # API endpoints & routes (v1)
├── .env.example            # Sample environment file
├── pyproject.toml          # Project configuration & dependencies
└── README.md               # Project documentation
```
