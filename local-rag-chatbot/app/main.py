from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.api.routes import router
<<<<<<< Updated upstream
from app.config import settings
=======

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
>>>>>>> Stashed changes

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)
<<<<<<< Updated upstream

# CORS middleware
=======
>>>>>>> Stashed changes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
<<<<<<< Updated upstream

# Include API routes
app.include_router(router, prefix="/api", tags=["API"])

# Mount static files
static_path = Path(__file__).parent.parent / "static"
templates_path = Path(__file__).parent.parent / "templates"

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/")
async def read_root():
    """Serve frontend"""
    return FileResponse(str(templates_path / "index.html"))
=======
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = Path("templates/index.html")
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Local RAG Assistant</h1><p>Template/index_file  not found</p>"
>>>>>>> Stashed changes

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.APP_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)