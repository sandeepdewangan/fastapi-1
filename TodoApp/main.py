from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from models import Todo
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from routers import auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Get the Auth Router
app.include_router(auth.router)


# After every API request db is closed.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# read_all depends on get_db, injected through DI
db_dependency = Annotated[Session, Depends(get_db)]

# API Request Class
class TodoRequest(BaseModel):
    title:str = Field(min_length=3, max_length=20)
    description:str = Field(min_length=3, max_length=100)
    priority:int = Field(ge=1, le=5)
    complete:bool


@app.get("/", status_code=status.HTTP_200_OK)
def read_all(db: db_dependency):
    return db.query(Todo).all()


@app.get("/todo/{id}", status_code=status.HTTP_200_OK)
def read_todo(db: db_dependency, id:int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todo", status_code=status.HTTP_201_CREATED)
def todo_create(db: db_dependency, todo:TodoRequest):
    newtodo = Todo(**todo.model_dump())
    db.add(newtodo)
    db.commit()

@app.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
def todo_update(db: db_dependency,  todo:TodoRequest, id:int):
    todo_model = db.query(Todo).filter(Todo.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

@app.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
def todo_delete(db: db_dependency,  id:int):
    todo_model = db.query(Todo).filter(Todo.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.query(Todo).filter(Todo.id == id).delete()
    db.commit()