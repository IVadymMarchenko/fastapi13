import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.dburl import config


class ManageSession:
    def __init__(self,url):
        self._engine=create_async_engine(url)
        self._session_maker= async_sessionmaker(autoflush=False,autocommit=False,bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception('No connect to DB')
        session=self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

session_manage=ManageSession(config.DB_URL)

async def get_db():
    async with session_manage.session() as session:
        yield session








# async def get_db():
#     engine = create_async_engine(config.DB_URL)
#     DBSession = async_sessionmaker(bind=engine)
#     async with DBSession() as session:
#         yield session
