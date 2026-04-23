from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from models import Todo
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


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

@router.get("/todo", status_code=status.HTTP_200_OK)
def read_all(user:user_dependency, db:db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
    return db.query(Todo).all()