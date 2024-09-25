from pydantic import BaseModel

class queryItem(BaseModel):
    userId : str
    query : str
