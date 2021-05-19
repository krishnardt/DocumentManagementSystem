from typing import List, Optional, Dict

from pydantic import BaseModel, EmailStr, ValidationError, validator
from fastapi import Form



class Users(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class User(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True

class Download(BaseModel):
	email_id: str
	filename: str

	class Config:
		orm_mode = True


class SharePost(BaseModel):
		collaborator_id: str
		filename: str
		access_level: str