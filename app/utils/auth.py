from fastapi import Request
from app.auth.auth_handler import decode_token

async def get_current_user(context):
    request: Request = context["request"]
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
        return decode_token(token)
    return None

def create_access_token(data: dict):
    from app.auth.auth_handler import create_access_token as generate_token
    return generate_token(data)