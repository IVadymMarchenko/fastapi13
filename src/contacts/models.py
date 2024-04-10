from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import String, Date, Column, create_engine, Integer, DateTime, func, ForeignKey, Boolean
from src.conf.dburl import config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
import asyncio

engine = create_async_engine(config.DB_URL)
DBSession = async_sessionmaker(bind=engine)
session = DBSession()
Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))
    surname: Mapped[str] = mapped_column(String(30))
    phone: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30))
    birthday = Column(Date, nullable=False)
    information: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    update_at: Mapped[date] = mapped_column('update_at', DateTime, default=func.now(), onupdate=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    user: Mapped['User'] = relationship('User',backref='contacts',lazy='joined')


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed:Mapped[bool]=mapped_column(Boolean,default=False)




async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Запуск сценария асинхронного создания таблиц
async def main():
    await create_tables()


# Запуск асинхронного сценария
if __name__ == '__main__':
    asyncio.run(main())
