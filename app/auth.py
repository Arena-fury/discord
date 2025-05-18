# app/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import Optional
from datetime import timedelta, datetime
from jose import jwt

SECRET = "supersecret"
router = APIRouter()

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str  # hashé !

engine = create_engine("sqlite:///db.sqlite")
SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as s:
        yield s

@router.post("/signup")
def signup(data: dict, db: Session = Depends(get_db)):
    if db.exec(select(User).where(User.username == data["username"])).first():
        raise HTTPException(400, "Utilisateur existe déjà")
    user = User(username=data["username"], password=data["password"])
    db.add(user); db.commit(); db.refresh(user)
    return {"msg": "ok"}

@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.username == data["username"])).first()
    if not user or user.password != data["password"]:
        raise HTTPException(401, "Mauvais identifiants")
    token = jwt.encode(
        {"sub": user.username, "exp": datetime.utcnow() + timedelta(hours=24)},
        SECRET,
        algorithm="HS256",
    )
    return {"access_token": token, "token_type": "bearer"}
