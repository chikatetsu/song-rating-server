from pydantic import BaseModel


class RateRequest(BaseModel):
    better_song: str
    worse_song: str

class StatusRequest(BaseModel):
    first_song: str
    second_song: str

class RateUpResponse(BaseModel):
    response: str

class RankObject(BaseModel):
    name: str
    score: float
    old_rank: int

class RankResponse(BaseModel):
    ranks: list[RankObject]

class SongInfoResponse(BaseModel):
    graph_rank: int
    elo_rank: int
    elo_score: float
    nb_upvotes: int
    nb_downvotes: int
    certitude: float

class StatusBetweenSongsResponse(BaseModel):
    song: str
    status: str
