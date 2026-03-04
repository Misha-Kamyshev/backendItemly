from fastapi import HTTPException

from .databases.repositories_sql.user import get_user

async def get_user_id(username: str) -> int:
    user = await get_user(username)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user["id"]
