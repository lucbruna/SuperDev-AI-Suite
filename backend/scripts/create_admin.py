#!/usr/bin/env python3
import argparse
import asyncio

from backend.users.model import User
from sqlalchemy import select

from backend.auth.passwords import hash_password
from backend.database.session import get_db


async def create_admin(email: str, password: str, username: str):
    async for session in get_db():
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"User {email} already exists")
            return

        admin = User(
            email=email,
            username=username,
            full_name="Administrator",
            hashed_password=hash_password(password),
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        session.add(admin)
        await session.commit()
        print(f"Admin user created: {email}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--email", default="admin@superdev.dev")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--username", default="admin")
    args = parser.parse_args()
    asyncio.run(create_admin(args.email, args.password, args.username))
