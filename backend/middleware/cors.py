from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(
    app: FastAPI,
    allow_origins: list[str] | None = None,
    allow_credentials: bool = True,
    allow_methods: list[str] | None = None,
    allow_headers: list[str] | None = None,
) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ["http://localhost:3000"],
        allow_credentials=allow_credentials,
        allow_methods=allow_methods or ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=allow_headers or ["Authorization", "Content-Type", "X-Request-ID"],
    )
