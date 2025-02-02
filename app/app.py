"""The app."""

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, repositories, index, webhooks
from app.log import get_logger

log = get_logger(__name__)

load_dotenv()


def create_app() -> FastAPI:
    fapp = FastAPI(title="elementary Bounties")

    log.info("✨ Starting elementary Bounties!")

    fapp.include_router(auth.router)
    fapp.include_router(repositories.router)
    fapp.include_router(index.router)
    fapp.include_router(webhooks.router)

    # For local development
    origins = [
        "http://localhost:3000",
    ]

    fapp.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Generic health route to sanity check the API
    @fapp.get("/health")
    async def health() -> str:
        return "ok"

    return fapp


app = create_app()
