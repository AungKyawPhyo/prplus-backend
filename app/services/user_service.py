from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    async def get_users(db: AsyncSession, skip=0, limit=10, name=None, role=None):
        # ✅ Eager load created_by and updated_by to avoid async lazy-loading issues
        query = (
            select(User)
            .options(
                selectinload(User.created_by),
                selectinload(User.updated_by)
            )
        )

        if name:
            query = query.where(User.name.ilike(f"%{name}%"))
        if role:
            query = query.where(User.role == role)

        # ✅ Get total count with subquery
        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total_count = total_result.scalar()

        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all(), total_count

    @staticmethod
    async def create_user(db: AsyncSession, input: dict, creator_id: int | None = None):
        if creator_id is not None:
            input["created_by_id"] = creator_id
        if "password" in input:
            input["password"] = pwd_context.hash(input["password"])

        user = User(**input)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, input: dict, updater_id: int):
        user = await db.get(User, user_id)
        if user:
            input["updated_by_id"] = updater_id
            for key, value in input.items():
                if key != "password":  # password not updated here
                    setattr(user, key, value)
            await db.commit()
            await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        user = await db.get(User, user_id)
        if user:
            await db.delete(user)
            await db.commit()
        return True