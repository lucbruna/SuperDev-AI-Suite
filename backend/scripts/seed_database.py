#!/usr/bin/env python3
import asyncio
import os
import secrets

from backend.users.model import User
from sqlalchemy import select

from backend.auth.passwords import hash_password
from backend.database.session import get_db


async def seed():
    async for session in get_db():
        result = await session.execute(select(User).where(User.email == "admin@superdev.dev"))
        existing = result.scalar_one_or_none()
        if existing:
            print("Admin user already exists")
            return

        # Never hardcode a known password. Use ADMIN_PASSWORD when provided,
        # otherwise generate a random one and print it once.
        admin_password = os.getenv("ADMIN_PASSWORD") or secrets.token_urlsafe(12)
        admin = User(
            email="admin@superdev.dev",
            username="admin",
            full_name="SuperDev Admin",
            hashed_password=hash_password(admin_password),
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        session.add(admin)
        await session.commit()
        print(f"Admin user created: admin@superdev.dev / {admin_password}")
        if not os.getenv("ADMIN_PASSWORD"):
            print("⚠️  Random password generated — set ADMIN_PASSWORD to control it and change it immediately.")


if __name__ == "__main__":
    asyncio.run(seed())
