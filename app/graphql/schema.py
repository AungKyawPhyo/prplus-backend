from ariadne import QueryType, MutationType, make_executable_schema, load_schema_from_path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.services.user_service import UserService
from app.auth.auth_handler import verify_password, create_access_token
from app.models.user import User
from app.services.event_service import EventService
from app.models.event import Event
from datetime import datetime
from app.auth.auth_handler import verify_password, create_access_token, hash_password

query = QueryType()
mutation = MutationType()

# Load SDL
type_defs = load_schema_from_path("app/graphql/schema.graphql")

# ----------- USER RESOLVERS -----------

@query.field("getUsers")
async def resolve_get_users(_, info, page=1, size=10, name=None, role=None):
    db: AsyncSession = info.context["request"].state.db
    current_user = info.context["request"].state.current_user
    if not current_user:
        raise Exception("Unauthorized")

    skip = (page - 1) * size
    users, total_count = await UserService.get_users(db, skip=skip, limit=size, name=name, role=role)
    return {"users": users, "totalCount": total_count}

# ✅ Added getUserById
@query.field("getUserById")
async def resolve_get_user_by_id(_, info, id: int):
    db: AsyncSession = info.context["request"].state.db
    current_user = info.context["request"].state.current_user
    if not current_user:
        raise Exception("Unauthorized")

    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    return user

@mutation.field("createUser")
async def resolve_create_user(_, info, input):
    db: AsyncSession = info.context["request"].state.db

    user_count = await db.scalar(select(func.count()).select_from(User))
    if user_count == 0:
        return await UserService.create_user(db, input, creator_id=None)

    current_user = info.context["request"].state.current_user
    if not current_user or info.context["request"].state.current_role != "manager":
        raise Exception("Unauthorized: Only manager can create users.")

    return await UserService.create_user(db, input, creator_id=current_user.id)

@mutation.field("updateUser")
async def resolve_update_user(_, info, id, input):
    role = info.context["request"].state.current_role
    if role != "manager":
        raise Exception("Unauthorized: Only manager can update users.")
    db: AsyncSession = info.context["request"].state.db
    current_user = info.context["request"].state.current_user
    return await UserService.update_user(db, id, input, updater_id=current_user.id)

@mutation.field("deleteUser")
async def resolve_delete_user(_, info, id):
    current_user = info.context["request"].state.current_user
    if not current_user or info.context["request"].state.current_role != "manager":
        raise Exception("Unauthorized  : Only manager can delete users.")
    db: AsyncSession = info.context["request"].state.db
    await UserService.delete_user(db, id)
    return True

@mutation.field("changePassword")
async def resolve_change_password(_, info, currentPassword: str, newPassword: str):
    db: AsyncSession = info.context["request"].state.db
    current_user = info.context["request"].state.current_user

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise Exception("User not found")
    if not verify_password(currentPassword, user.password):
        raise Exception("Current password is incorrect")

    # ✅ use common hash_password for consistency
    user.password = hash_password(newPassword)
    await db.commit()
    return True

@mutation.field("login")
async def resolve_login(_, info, username, password):
    db: AsyncSession = info.context["request"].state.db
    result = await db.execute(select(User).where(User.name == username))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password):
        return create_access_token({"sub": user.name, "role": user.role})
    return None

# ----------- EVENT RESOLVERS -----------
@query.field("getEvents")
async def resolve_get_events(_, info, page=1, size=10, name=None, contact=None, venue=None, dateFrom=None, dateTo=None):
    db: AsyncSession = info.context["request"].state.db
    skip = (page - 1) * size
    events, total_count = await EventService.get_events(
        db,
        skip=skip,
        limit=size,
        name=name,
        contact=contact,
        venue=venue,
        date_from=dateFrom,
        date_to=dateTo,
    )
    return {"events": events, "totalCount": total_count}

@mutation.field("createEvent")
async def resolve_create_event(_, info, input):
    role = info.context["request"].state.current_role
    if role not in ["manager", "staff"]:
        raise Exception("Unauthorized: Only manager can create events.")
    db: AsyncSession = info.context["request"].state.db
    current_user = info.context["request"].state.current_user
    return await EventService.create_event(db, input, user_id=current_user.id)

@mutation.field("bulkCreateEvents")
async def resolve_bulk_create_events(_, info, events):
    role = info.context["request"].state.current_role
    if role not in ["manager", "staff"]:
        raise Exception("Unauthorized: Only manager can bulk import events.")
    db: AsyncSession = info.context["request"].state.db
    current_user = info.context["request"].state.current_user
    return await EventService.bulk_create_events(db, events, user_id=current_user.id)

@mutation.field("updateEvent")
async def resolve_update_event(_, info, id, input):
    role = info.context["request"].state.current_role
    if role not in ["manager", "staff"]:
        raise Exception("Unauthorized: Only manager can update events.")
    db: AsyncSession = info.context["request"].state.db
    current_user = info.context["request"].state.current_user
    return await EventService.update_event(db, id, input, user_id=current_user.id)

@mutation.field("deleteEvent")
async def resolve_delete_event(_, info, id):
    role = info.context["request"].state.current_role
    if role != "manager":
        raise Exception("Unauthorized: Only manager can delete events.")
    db: AsyncSession = info.context["request"].state.db
    return await EventService.delete_event(db, id)

@query.field("getEventById")
async def resolve_get_event_by_id(_, info, id: int):
    db: AsyncSession = info.context["request"].state.db
    current_user = info.context["request"].state.current_user
    if not current_user:
        raise Exception("Unauthorized")

    event = await EventService.get_event_by_id(db, event_id=id)
    return event

# ----------- FINAL SCHEMA -----------
schema = make_executable_schema(type_defs, [query, mutation])