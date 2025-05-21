from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    cpf: str


class UserSchemaCreate(UserSchema):
    password: str


class UserSchemaUpdate(UserSchema):
    password: str | None = None


class UserPublic(UserSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: List[UserPublic]


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    message: str
