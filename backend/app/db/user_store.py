import aiosqlite
import uuid
from passlib.hash import bcrypt

DB_PATH = "./data/chat_history.db"


async def init_users_table():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        await db.commit()


async def create_user(email: str, name: str, password: str) -> dict | None:
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hash(password)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO users (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
                (user_id, email.lower(), name, password_hash),
            )
            await db.commit()
        return {"id": user_id, "email": email.lower(), "name": name}
    except Exception:
        return None


async def authenticate_user(email: str, password: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, email, name, password_hash FROM users WHERE email = ?",
            (email.lower(),),
        )
        row = await cursor.fetchone()
        if row and bcrypt.verify(password, row["password_hash"]):
            return {"id": row["id"], "email": row["email"], "name": row["name"]}
    return None


async def get_user_by_id(user_id: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, email, name FROM users WHERE id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
