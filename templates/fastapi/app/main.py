from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import health, projects

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API powered by SuperDev",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])


@app.get("/")
async def root():
    return {"message": "Welcome to {{project_name}}", "version": settings.VERSION}
