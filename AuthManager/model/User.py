from pydantic import BaseModel

class User(BaseModel):
    userId: str
    password: str
    name: str
    
class UserLoginRequest(BaseModel):
    userId: str
    password: str
