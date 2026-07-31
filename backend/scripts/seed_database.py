#!/usr/bin/env python3
import asyncio

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

        admin = User(
            email="admin@superdev.dev",
            username="admin",
            full_name="SuperDev Admin",
            hashed_password=hash_password("admin123"),
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        session.add(admin)
        await session.commit()
        print("Admin user created: admin@superdev.dev / admin123")


if __name__ == "__main__":
    asyncio.run(seed())
