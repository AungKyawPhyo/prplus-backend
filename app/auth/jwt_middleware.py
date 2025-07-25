from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth.auth_handler import decode_access_token
from app.db.database import SessionLocal
from app.models.user import User
from sqlalchemy.future import select

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        request.state.current_user = None
        request.state.current_role = None

        if token and token.startswith("Bearer "):
            payload = decode_access_token(token.split(" ")[1])
            if payload:
                async with SessionLocal() as db:
                    result = await db.execute(select(User).where(User.name == payload.get("sub")))
                    user_obj = result.scalar_one_or_none()
                    if user_obj:
                        request.state.current_user = user_obj
                        request.state.current_role = user_obj.role

        response = await call_next(request)
        return response