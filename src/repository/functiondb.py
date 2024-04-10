import sys

from sqlalchemy import select, cast, Date, or_, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from src.contacts.models import Contact, User
from src.schemas.checkschemas import CreateContactSchema, CreateContact
from datetime import datetime, timedelta
from sqlalchemy import func


async def get_contacts(limit: int, offset: int, db: AsyncSession,user: User):
    smt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(smt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession,user: User):
    smt = select(Contact).filter_by(id=contact_id,user=user)
    contact = await db.execute(smt)
    return contact.scalar_one_or_none()


async def create_contact(body: CreateContactSchema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True),user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: CreateContactSchema, db: AsyncSession,user: User):
    smt = select(Contact).filter_by(id=contact_id,user=user)
    contacts = await db.execute(smt)
    contact = contacts.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.phone = body.phone
        contact.email = body.email
        contact.birthday = body.birthday
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    smt = select(Contact).filter_by(id=contact_id)
    contacts = await db.execute(smt)
    contact = contacts.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def upcoming_birthday(db: AsyncSession):
    """Повертає список контактів, у яких день народження протягом наступних 7 днів."""

    today = datetime.today().date()
    week_from_now = today + timedelta(days=3)

    # Запит до бази даних для отримання контактів з днями народження у межах наступних 7 днів
    stmt = select(Contact).filter(
        or_(
            and_(
                extract('month', Contact.birthday) == today.month,
                extract('day', Contact.birthday) >= today.day
            ),
            and_(
                extract('month', Contact.birthday) == week_from_now.month,
                extract('day', Contact.birthday) <= week_from_now.day
            ),
            and_(
                extract('month', Contact.birthday) == (today.month + 1) % 12,
                extract('day', Contact.birthday) <= week_from_now.day
            )
        )
    )

    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def look_for_contact(db: AsyncSession, name_contact: str):
    query = select(Contact).filter(or_(Contact.name == name_contact,
                                       Contact.surname == name_contact,
                                       Contact.email == name_contact))
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    return contact
