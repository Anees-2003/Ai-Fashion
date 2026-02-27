import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from routes import design, upload, recommend, products, history
from routes.auth import router as auth_router

app = FastAPI(
    title="AI Fashion Design Generator",
    description="Generate clothing designs from text and get AI-powered outfit recommendations.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        os.getenv("ALLOWED_ORIGIN", "https://your-frontend.vercel.app"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve all uploaded files (photos, AI designs, previews)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
for sub in ["", "designs", "previews"]:
    os.makedirs(os.path.join(UPLOAD_DIR, sub) if sub else UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Register routers
app.include_router(design.router,   prefix="/api", tags=["Design"])
app.include_router(upload.router,   prefix="/api", tags=["Upload"])
app.include_router(recommend.router,prefix="/api", tags=["Recommend"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(auth_router,    prefix="/api", tags=["Auth"])


@app.get("/")
async def root():
    return {"message": "AI Fashion Studio API v2", "docs": "/docs", "version": "2.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
