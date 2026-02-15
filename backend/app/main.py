from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, legacy, memories, objects, upload, vision, voice, toolkit


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Memory Anchors API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Legacy routes (no prefix — keeps frontend working)
app.include_router(legacy.router, tags=["legacy"])

# V1 API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(memories.router, prefix="/api/v1/memories", tags=["memories"])
app.include_router(objects.router, prefix="/api/v1/objects", tags=["objects"])
app.include_router(vision.router, prefix="/api/v1/vision", tags=["vision"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["voice"])
app.include_router(toolkit.router, prefix="/api/v1/toolkit", tags=["toolkit"])

# Upload routes (no api/v1 prefix for simplicity with frontend)
app.include_router(upload.router, tags=["upload"])
