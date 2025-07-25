from app.models.event import Event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime

class EventService:
    @staticmethod
    async def get_events(db: AsyncSession, skip=0, limit=10, name=None, contact=None, venue=None, date_from=None, date_to=None):
        query = select(Event)

        # ✅ Apply filters
        if name:
            query = query.where(Event.name.ilike(f"%{name}%"))
        if contact:
            query = query.where(Event.contact.ilike(f"%{contact}%"))
        if venue:
            query = query.where(Event.venue.ilike(f"%{venue}%"))
        if date_from:
            df = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.where(Event.event_date >= df)
        if date_to:
            dt = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.where(Event.event_date <= dt)

        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total_count = total_result.scalar()

        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all(), total_count

    @staticmethod
    async def get_event_by_id(db: AsyncSession, event_id: int):
        result = await db.execute(select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_event(db: AsyncSession, input: dict, user_id: int):
        if "event_date" in input and isinstance(input["event_date"], str):
            input["event_date"] = datetime.strptime(input["event_date"], "%Y-%m-%d")

        event = Event(**input, created_by_id=user_id)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def update_event(db: AsyncSession, event_id: int, input: dict, user_id: int):
        if "event_date" in input and isinstance(input["event_date"], str):
            input["event_date"] = datetime.strptime(input["event_date"], "%Y-%m-%d")

        event = await db.get(Event, event_id)
        if event:
            for key, value in input.items():
                setattr(event, key, value)
            event.updated_by_id = user_id
            await db.commit()
            await db.refresh(event)
        return event

    @staticmethod
    async def delete_event(db: AsyncSession, event_id: int):
        event = await db.get(Event, event_id)
        if event:
            await db.delete(event)
            await db.commit()
        return True

    @staticmethod
    async def bulk_create_events(db: AsyncSession, events: list, user_id: int):
        parsed_events = []
        for ev in events:
            if "event_date" in ev and isinstance(ev["event_date"], str):
                ev["event_date"] = datetime.strptime(ev["event_date"], "%Y-%m-%d")
            parsed_events.append(Event(**ev, created_by_id=user_id))
        db.add_all(parsed_events)
        await db.commit()
        return True