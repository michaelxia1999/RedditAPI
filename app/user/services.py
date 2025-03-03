from app.auth.services import verify_hashed_password
from app.db.schema import User
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(
    username: str, password: str, email: str, display_name: str, avatar: str, db: AsyncSession
) -> User:
    query = (
        insert(User)
        .values(
            username=username,
            password=password,
            email=email,
            display_name=display_name,
            avatar=avatar,
        )
        .returning(User)
    )
    result = await db.execute(query)
    user = result.scalars().one()
    return user


async def get_user(user_id: int, db: AsyncSession) -> User | None:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    return user


async def update_user(user_id: int, user_data: dict, db: AsyncSession) -> User | None:
    query = update(User).where(User.id == user_id).values(**user_data).returning(User)
    result = await db.execute(query)
    user = result.scalars().first()
    return user


async def delete_user(user_id: int, db: AsyncSession) -> bool:
    query = delete(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.rowcount > 0


async def username_exists(username: str, db: AsyncSession) -> bool:
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()

    return True if user else False


async def display_name_exists(display_name: str, db: AsyncSession) -> bool:
    query = select(User).where(User.display_name == display_name)
    result = await db.execute(query)
    user = result.scalars().first()

    return True if user else False


async def email_exists(email: str, db: AsyncSession) -> bool:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalars().first()

    return True if user else False


async def get_user_id_by_credentials(username: str, password: str, db: AsyncSession) -> int | None:
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        return None

    if not verify_hashed_password(password=password, hashed_password=user.password):
        return None

    return user.id
