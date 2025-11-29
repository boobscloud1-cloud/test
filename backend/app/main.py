from fastapi import FastAPI
from app.routers import users, tasks, game, auth, admin
from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title="Wheel of Fortune MiniApp")

# CORS for Frontend (configured via env ALLOW_ORIGINS, comma-separated or "*" for dev)
origins = ["*"] if settings.ALLOW_ORIGINS == "*" else [o.strip() for o in settings.ALLOW_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # No cookies-based auth; safer default
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(game.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup():
    # Init DB Tables
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # RESET DB (Dev only)
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "MiniApp Backend Running"}
