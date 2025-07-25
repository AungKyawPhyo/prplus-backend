from fastapi.middleware.cors import CORSMiddleware
from app.db.database import get_db, engine, Base, SessionLocal
from app.graphql.schema import schema
from ariadne.asgi import GraphQL
from fastapi import FastAPI, Request
from app.auth.jwt_middleware import JWTMiddleware


app = FastAPI()
app.add_middleware(JWTMiddleware)

graphql_app = GraphQL(schema, debug=True)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    await request.state.db.close()
    return response

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.mount("/graphql", graphql_app)