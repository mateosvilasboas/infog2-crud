# from http import HTTPStatus
# from typing import List

# from fastapi import HTTPException
# from pydantic import BaseModel, ConfigDict, field_validator
# from validate_docbr import CPF


# class ProductSchema(BaseModel):
#     name: str


# class UserSchemaCreate(UserSchema):
#     cpf: str
#     password: str

#     @field_validator('cpf', mode='before')
#     @classmethod
#     def cpf_validation(cls, value: str) -> str:
#         cpf = CPF()
#         if not cpf.validate(value):
#             raise HTTPException(
#                 status_code=HTTPStatus.BAD_REQUEST, detail='Invalid CPF'
#             )
#         return value


# class UserSchemaUpdate(UserSchema):
#     password: str | None = None


# class UserPublic(UserSchema):
#     id: int
#     cpf: str
#     model_config = ConfigDict(from_attributes=True)


# class UserList(BaseModel):
#     users: List[UserPublic]
