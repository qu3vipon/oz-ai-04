from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


DATABASE_URL = "mysql+aiomysql://root:password@db:3306/fastapi"
engine = create_async_engine(DATABASE_URL)
SessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

async def get_session():
    session = SessionFactory()
    try:
        yield session
    finally:
        await session.close()
