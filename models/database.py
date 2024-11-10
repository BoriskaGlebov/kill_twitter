from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///recipes.db"

async_engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
# async_session=async_sessionmaker(engine,expire_on_commit=False)
# session=async_session
Base = declarative_base()

# print(type(async_session))
