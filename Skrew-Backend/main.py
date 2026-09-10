import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "Skrew-Frontend"
DB_PATH = BASE_DIR / "Skrew-Backend" / "skrew.db"

AVATAR_COLORS = ['#FF6B35', '#5B8DEF', '#22A06B', '#A855F7', '#EC4899', '#14B8A6', '#F59E0B']


class SessionCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
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


def init_db() -> None:
    with get_db() as conn:
        cur = conn.cursor()
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
                    _now_iso()
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
                    _now_iso()
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
                    _now_iso()
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
                    _now_iso()
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    }


def list_sessions() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM sessions ORDER BY id DESC"
        )
        rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def create_session(data: SessionCreate) -> Dict[str, Any]:
    import random

    avatar_color = random.choice(AVATAR_COLORS)
    post_time = "Just now"
    created_at = _now_iso()

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sessions (
                username, spot_name, address, date, time, skill,
                notes, avatar_color, post_time, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.username,
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
        cur.execute("SELECT * FROM sessions WHERE id = ?", (new_id,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create session")
    return _row_to_dict(row)


init_db()

app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_DIR / "assets"),
    name="assets"
)


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/dashboard.html")
def dashboard_page():
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@app.get("/api/dashboard")
def api_dashboard():
    sessions = list_sessions()
    return {"sessions": sessions}


@app.post("/api/sessions", status_code=201)
def api_create_session(data: SessionCreate):
    session = create_session(data)
    return {"session": session}


@app.get("/health")
def health_check():
    return {"status": "ok"}
