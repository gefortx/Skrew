import os
import random
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from auth import (  # noqa: E402
    create_access_token,
    decode_access_token,
    get_bearer_token,
    hash_password,
    require_jwt_secret,
    verify_password,
)

app = FastAPI()

FRONTEND_DIR = BASE_DIR / "Skrew-Frontend"
DB_PATH = BASE_DIR / "Skrew-Backend" / "skrew.db"

AVATAR_COLORS = ["#FF6B35", "#5B8DEF", "#22A06B", "#A855F7", "#EC4899", "#14B8A6", "#F59E0B"]

SESSION_SELECT = """
    SELECT
        s.id,
        COALESCE(u.username, s.username) AS username,
        s.spot_name,
        s.address,
        s.date,
        s.time,
        s.skill,
        s.notes,
        s.avatar_color,
        s.post_time,
        s.created_at,
        s.user_id
    FROM sessions s
    LEFT JOIN users u ON u.id = s.user_id
"""


class UserCredentials(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def username_format(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Username is required")
        if not cleaned.replace("_", "").isalnum() or not all(
            ch.isalnum() or ch == "_" for ch in cleaned
        ):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return cleaned


class SessionCreate(BaseModel):
    spotName: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=300)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    skill: str = Field(..., min_length=1, max_length=32)
    notes: str = Field(default="", max_length=2000)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _column_names(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [row["name"] for row in cur.fetchall()]


def init_db() -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                spot_name TEXT NOT NULL,
                address TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                skill TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                avatar_color TEXT NOT NULL,
                post_time TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        session_columns = _column_names(conn, "sessions")
        if "user_id" not in session_columns:
            cur.execute(
                "ALTER TABLE sessions ADD COLUMN user_id INTEGER REFERENCES users(id)"
            )

        cur.execute("SELECT COUNT(*) AS cnt FROM sessions")
        count = cur.fetchone()["cnt"]
        if count == 0:
            seed_sessions = [
                (
                    "skate_mia",
                    "Westside Ledge Spot",
                    "420 Oak Ave, Westside",
                    "2026-09-12",
                    "15:00",
                    "Intermediate",
                    "Bring wax! Ledges are primo today 🔥",
                    "#FF6B35",
                    "2 hours ago",
                    _now_iso(),
                ),
                (
                    "riley_shreds",
                    "Downtown 12 Stair",
                    "12th & Main, Downtown",
                    "2026-09-13",
                    "12:00",
                    "Advanced",
                    "Session before the rain. Big tricks only.",
                    "#5B8DEF",
                    "5 hours ago",
                    _now_iso(),
                ),
                (
                    "jordan_cruise",
                    "Community Skate Park",
                    "Riverside Park, East End",
                    "2026-09-11",
                    "17:00",
                    "All Levels",
                    "Beginner friendly clinic + free skate. Come through!",
                    "#22A06B",
                    "1 day ago",
                    _now_iso(),
                ),
                (
                    "sam_gaps",
                    "River Gap Spot",
                    "Riverwalk Underpass",
                    "2026-09-12",
                    "18:00",
                    "Advanced",
                    "Gap is dry finally. Sunset session.",
                    "#A855F7",
                    "3 hours ago",
                    _now_iso(),
                ),
            ]
            cur.executemany(
                """
                INSERT INTO sessions (
                    username, spot_name, address, date, time, skill,
                    notes, avatar_color, post_time, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                seed_sessions,
            )


def _user_public(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "username": row["username"],
        "created_at": row["created_at"],
    }


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "username": row["username"],
        "spotName": row["spot_name"],
        "address": row["address"],
        "date": row["date"],
        "time": row["time"],
        "skill": row["skill"],
        "notes": row["notes"],
        "avatarColor": row["avatar_color"],
        "postTime": row["post_time"],
        "createdAt": row["created_at"],
        "userId": row["user_id"] if "user_id" in row.keys() else None,
    }


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash, created_at FROM users WHERE id = ?",
            (user_id,),
        )
        return cur.fetchone()


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
            (username,),
        )
        return cur.fetchone()


def get_current_user(token: str = Depends(get_bearer_token)) -> Dict[str, Any]:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        parsed_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    row = get_user_by_id(parsed_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _user_public(row)


def list_sessions() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(SESSION_SELECT + " ORDER BY s.id DESC")
        rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def create_session(data: SessionCreate, user: Dict[str, Any]) -> Dict[str, Any]:
    avatar_color = random.choice(AVATAR_COLORS)
    post_time = "Just now"
    created_at = _now_iso()

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sessions (
                username, user_id, spot_name, address, date, time, skill,
                notes, avatar_color, post_time, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["username"],
                user["id"],
                data.spotName,
                data.address,
                data.date,
                data.time,
                data.skill,
                data.notes,
                avatar_color,
                post_time,
                created_at,
            ),
        )
        new_id = cur.lastrowid
        cur.execute(SESSION_SELECT + " WHERE s.id = ?", (new_id,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create session")
    return _row_to_dict(row)


require_jwt_secret()
init_db()

app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_DIR / "assets"),
    name="assets",
)


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/dashboard.html")
def dashboard_page():
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@app.get("/login.html")
@app.get("/login")
def login_page():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/register.html")
@app.get("/register")
def register_page():
    return FileResponse(FRONTEND_DIR / "register.html")


@app.post("/register", status_code=201)
@app.post("/api/register", status_code=201)
def api_register(data: UserCredentials):
    existing = get_user_by_username(data.username)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    created_at = _now_iso()
    password_hash = hash_password(data.password)
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO users (username, password_hash, created_at)
                VALUES (?, ?, ?)
                """,
                (data.username, password_hash, created_at),
            )
            new_id = cur.lastrowid
            cur.execute(
                "SELECT id, username, created_at FROM users WHERE id = ?",
                (new_id,),
            )
            row = cur.fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return {"message": "Account created", "user": _user_public(row)}


@app.post("/login")
@app.post("/api/login")
def api_login(data: UserCredentials):
    user = get_user_by_username(data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
        )
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    token = create_access_token(user["id"], user["username"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _user_public(user),
    }


@app.get("/api/me")
def api_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": current_user}


@app.get("/api/dashboard")
def api_dashboard():
    sessions = list_sessions()
    return {"sessions": sessions}


@app.post("/api/sessions", status_code=201)
def api_create_session(
    data: SessionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    session = create_session(data, current_user)
    return {"session": session}


@app.get("/health")
def health_check():
    return {"status": "ok"}
