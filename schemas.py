from pydantic import BaseModel
from typing import Optional


class UserRequestModel(BaseModel):
    username:str
    email: Optional[str] = None
    

class UserResponseModel(UserRequestModel):
    id:int
    

class FamiliaRequestModel(BaseModel):
    id:int