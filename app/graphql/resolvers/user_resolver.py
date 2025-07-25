from ariadne import QueryType, MutationType
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from sqlalchemy import select,func  # ✅ REQUIRED!

query = QueryType()
mutation = MutationType()

@query.field("getUsers")
async def resolve_get_users(_, info, page=1, size=10):
    db = info.context["db"]
    skip = (page - 1) * size
    return await UserService.get_users(db, skip, size)

@query.field("currentUser")
async def resolve_current_user(_, info):
    return info.context.get("user")

@mutation.field("createUser")
async def resolve_create_user(_, info, input):
    db = info.context["db"]
    data = UserCreate(**input)

    # ✅ Allow first user creation without auth
    user_count = await db.scalar(select(func.count()).select_from(User))
    if user_count == 0:
        return await UserService.create_user(db, data.dict(), creator_id=None)

    # 🔐 Require token for subsequent users
    current_user = info.context.get("user")
    if not current_user:
        raise Exception("Unauthorized: Please login to create users")

    return await UserService.create_user(db, data.dict(), creator_id=current_user["id"])

@mutation.field("updateUser")
async def resolve_update_user(_, info, id, input):
    db = info.context["db"]
    user = info.context.get("user")
    data = UserUpdate(**input)
    return await UserService.update_user(db, id, data.dict(), updater_id=user["id"])

@mutation.field("deleteUser")
async def resolve_delete_user(_, info, id):
    db = info.context["db"]
    user = info.context.get("user")
    if user["role"] != "manager":
        raise Exception("Unauthorized: Only managers can delete users")
    return await UserService.delete_user(db, id)