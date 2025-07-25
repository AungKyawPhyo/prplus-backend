from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ⛔ Old Local Config (commented out)
# DATABASE_URL = "postgresql+asyncpg://postgres:akphyo93@localhost/prplus_db"

# ✅ Hardcoded Render PostgreSQL URL
DATABASE_URL = "postgresql+asyncpg://prplus_db_user:VVwrtlDuGEnjUWKerx8CfVjcybSiN9lK@dpg-d220llfgi27c73ef2aqg-a.singapore-postgres.render.com/prplus_db"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session