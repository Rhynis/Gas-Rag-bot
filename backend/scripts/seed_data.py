"""Load local seed data into the development database."""

import asyncio
from pathlib import Path

from sqlalchemy import text

from app.db.session import AsyncSessionLocal


async def main() -> None:
    """Execute the SQL seed file."""
    seed_path = Path(__file__).resolve().parents[1] / "data" / "seed.sql"
    sql = seed_path.read_text(encoding="utf-8")
    async with AsyncSessionLocal() as session:
        await session.execute(text(sql))
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
