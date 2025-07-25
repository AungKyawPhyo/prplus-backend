from ariadne import QueryType, MutationType
from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventUpdate

query = QueryType()
mutation = MutationType()

@query.field("getEvents")
async def resolve_get_events(_, info, skip=0, limit=10):
    db = info.context["db"]
    return await EventService.get_events(db, skip, limit)

@query.field("getEventById")
async def resolve_get_event_by_id(_, info, id):
    db = info.context["db"]
    return await EventService.get_event_by_id(db, id)

@mutation.field("createEvent")
async def resolve_create_event(_, info, input):
    db = info.context["db"]
    user = info.context.get("user")
    if user["role"] != "manager":
        raise Exception("Unauthorized: Only managers can create events")
    data = EventCreate(**input)
    return await EventService.create_event(db, data.dict(), user["id"])

@mutation.field("updateEvent")
async def resolve_update_event(_, info, id, input):
    db = info.context["db"]
    user = info.context.get("user")
    if user["role"] != "manager":
        raise Exception("Unauthorized: Only managers can update events")
    data = EventUpdate(**input)
    return await EventService.update_event(db, id, data.dict(), user["id"])

@mutation.field("deleteEvent")
async def resolve_delete_event(_, info, id):
    db = info.context["db"]
    user = info.context.get("user")
    if user["role"] != "manager":
        raise Exception("Unauthorized: Only managers can delete events")
    await EventService.delete_event(db, id)
    return True