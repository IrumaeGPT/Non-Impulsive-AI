from pydantic import BaseModel

class updateEpisodeItem(BaseModel):
    userId : str
    summary : str
