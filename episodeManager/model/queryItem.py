from pydantic import BaseModel

class queryItem(BaseModel):
    userId : str
    querys : list
