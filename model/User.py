from pydantic import BaseModel

class Item(BaseModel):
    userId: str
    observation: str
    importance: float
    contextValid: bool
    query : str

    
class User(BaseModel):
    userId: str