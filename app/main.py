from fastapi import FastAPI

from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic Todo", description="Todo app with agentic skill recommendations")
