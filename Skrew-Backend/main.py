from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "Skrew-Frontend"

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
    sessions = [
        {
            "username": "skate_mia",
            "spotName": "Westside Ledge Spot",
            "address": "420 Oak Ave, Westside",
            "date": "2026-09-12",
            "time": "15:00",
            "skill": "Intermediate",
            "notes": "Bring wax! Ledges are primo today 🔥",
            "avatarColor": "#FF6B35",
            "postTime": "2 hours ago"
        },
        {
            "username": "riley_shreds",
            "spotName": "Downtown 12 Stair",
            "address": "12th & Main, Downtown",
            "date": "2026-09-13",
            "time": "12:00",
            "skill": "Advanced",
            "notes": "Session before the rain. Big tricks only.",
            "avatarColor": "#5B8DEF",
            "postTime": "5 hours ago"
        },
        {
            "username": "jordan_cruise",
            "spotName": "Community Skate Park",
            "address": "Riverside Park, East End",
            "date": "2026-09-11",
            "time": "17:00",
            "skill": "All Levels",
            "notes": "Beginner friendly clinic + free skate. Come through!",
            "avatarColor": "#22A06B",
            "postTime": "1 day ago"
        },
        {
            "username": "sam_gaps",
            "spotName": "River Gap Spot",
            "address": "Riverwalk Underpass",
            "date": "2026-09-12",
            "time": "18:00",
            "skill": "Advanced",
            "notes": "Gap is dry finally. Sunset session.",
            "avatarColor": "#A855F7",
            "postTime": "3 hours ago"
        }
    ]
    return {"sessions": sessions}


@app.get("/health")
def health_check():
    return {"status": "ok"}