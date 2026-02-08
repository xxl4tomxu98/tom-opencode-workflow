from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routers import api, web

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic Todo", description="Todo app with agentic skill recommendations")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api.router)
app.include_router(web.router)
