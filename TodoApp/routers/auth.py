from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users

from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

router =  APIRouter()

# Generate random secret key
# openssl rand -hex 32
SECRET_KEY = '51a53e78df31dec029ca6d3659103b26fbf504555ff2520f6cda90faf89ef9f6'
ALGORITHM = 'HS256'


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    email:str
    username:str
    first_name:str
    last_name:str
    password:str
    role:str

class Token(BaseModel):
    access_token: str
    token_type: str

def authenticate_user(username:str, password:str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    return user

def create_access_token(username:str, user_id:int, expires_delta:timedelta):
    encode = {'sub':username, 'id':user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/auth", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, user_req: CreateUserRequest):
    user = Users(
        email = user_req.email,
        username = user_req.username,
        first_name = user_req.first_name,
        last_name = user_req.last_name,
        hashed_password = user_req.password,
        role = user_req.role,
        is_active=True
    )
    db.add(user)
    db.commit()

@router.post("/token", response_model=Token)
def login_for_acces_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return 'Failed Authentication'
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type':'bearer'}

