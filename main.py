import os
import sys

# Ensure current directory and project root are in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(project_root, "app")

for p in [project_root, app_dir, os.getcwd()]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

# Flexible imports to support both nested app/ structure and flat GitHub upload
try:
    from app.database import engine, Base, SessionLocal
except ModuleNotFoundError:
    from database import engine, Base, SessionLocal

try:
    from app.api import exam_types, exams, dashboard, course_analysis, goals, report, demo, auth, planner
except ModuleNotFoundError:
    import exam_types, exams, dashboard, course_analysis, goals, report, demo, auth, planner

try:
    from app.services.demo_data_service import DemoDataService
except ModuleNotFoundError:
    try:
        from services.demo_data_service import DemoDataService
    except ModuleNotFoundError:
        from demo_data_service import DemoDataService

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            try:
                from app.models import ExamType
            except ModuleNotFoundError:
                from models import ExamType
                
            if not db.query(ExamType).first():
                print("PusulamNet ilklendiriliyor: Hazır sınav türleri yükleniyor...")
                DemoDataService.init_predefined_types_only(db)
        finally:
            db.close()
    except Exception as e:
        print(f"PusulamNet ilklendirme uyarısı: {e}")
    yield

app = FastAPI(
    title="PusulamNet - Öğrenci Deneme Takip ve Analiz Sistemi",
    description="Öğrenciler için deneme net hesabı, istatistiksel analiz ve gelişim takip platformu",
    version="1.0.0",
    lifespan=lifespan
)

# Routers
app.include_router(auth.router)
app.include_router(exam_types.router)
app.include_router(exams.router)
app.include_router(dashboard.router)
app.include_router(course_analysis.router)
app.include_router(goals.router)
app.include_router(report.router)
app.include_router(planner.router)
app.include_router(demo.router)

# Create database tables automatically
Base.metadata.create_all(bind=engine)

# Mount static directory if exists
static_candidates = [
    os.path.join(project_root, "static"),
    os.path.join(os.path.dirname(project_root), "static"),
    os.path.join(os.getcwd(), "static"),
    project_root,
    os.getcwd()
]

for s_dir in static_candidates:
    if os.path.exists(s_dir) and os.path.isdir(s_dir) and os.path.exists(os.path.join(s_dir, "js")):
        try:
            app.mount("/static", StaticFiles(directory=s_dir), name="static")
            break
        except Exception:
            pass

@app.get("/")
def read_root():
    candidates = [
        os.path.join(project_root, "index.html"),
        os.path.join(os.path.dirname(project_root), "index.html"),
        os.path.join(project_root, "static", "index.html"),
        os.path.join(os.path.dirname(project_root), "static", "index.html"),
        os.path.join(os.getcwd(), "index.html"),
        os.path.join(os.getcwd(), "static", "index.html")
    ]
    for candidate in candidates:
        if os.path.exists(candidate) and os.path.isfile(candidate):
            return FileResponse(candidate, headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            })
    return {"message": "PusulamNet API çalışıyor."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
