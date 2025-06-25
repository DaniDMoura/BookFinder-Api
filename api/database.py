from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from api.settings import Settings

settings = Settings()
engine = create_async_engine(settings.DATABASE_URL, echo=True, echo_pool=True)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with async_session() as session:
        yield session
