from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    
    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str
    description: str
    status: Optional[str] = "pending"

class Task(TaskCreate):
    id: int
    created_at: str
    owner_id: int
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
