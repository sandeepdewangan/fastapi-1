from fastapi import FastAPI
from models import Todo
import models
from database import engine, SessionLocal
from routers import auth, todos

app = FastAPI()

# Create DB
models.Base.metadata.create_all(bind=engine)

# Get the Router
app.include_router(auth.router)
app.include_router(todos.router)

