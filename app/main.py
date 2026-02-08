from fastapi import FastAPI

from app.database import engine, Base
from app.routers import api

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic Todo", description="Todo app with agentic skill recommendations")

app.include_router(api.router)
