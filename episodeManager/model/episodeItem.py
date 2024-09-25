from pydantic import BaseModel

class episodeItem(BaseModel):
    userId: str
    observation: str