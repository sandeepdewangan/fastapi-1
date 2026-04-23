from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from models import Todo
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user

router = APIRouter()


# After every API request db is closed.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# read_all depends on get_db, injected through DI
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)];

# API Request Class
class TodoRequest(BaseModel):
    title:str = Field(min_length=3, max_length=20)
    description:str = Field(min_length=3, max_length=100)
    priority:int = Field(ge=1, le=5)
    complete:bool


@router.get("/todos", status_code=status.HTTP_200_OK)
def read_all(db: db_dependency):
    return db.query(Todo).all()


@router.get("/todos/{id}", status_code=status.HTTP_200_OK)
def read_todo(db: db_dependency, id:int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post("/todos", status_code=status.HTTP_201_CREATED)
def todo_create(user:user_dependency, db: db_dependency, todo:TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")
    newtodo = Todo(**todo.model_dump(), owner_id=user.get('id'))
    db.add(newtodo)
    db.commit()

@router.put("/todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
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

@router.delete("/todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def todo_delete(db: db_dependency,  id:int):
    todo_model = db.query(Todo).filter(Todo.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.query(Todo).filter(Todo.id == id).delete()
    db.commit()