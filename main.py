from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from os import getenv

from app.dto import RateRequest, StatusRequest, RateUpResponse, RankResponse, SongInfoResponse
from app.rates_cache import RatesCache
from app.service import get_certitude, get_status_between_songs


load_dotenv()
AUTH_TOKEN = getenv("AUTH_TOKEN", "")
IS_DEV = getenv("DEV") is not None

cache = RatesCache()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    cache.db.disconnect()

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if IS_DEV else None,
    redoc_url="/redoc" if IS_DEV else None,
    openapi_url="/openapi.json" if IS_DEV else None,
)
security = HTTPBearer(auto_error=False)

def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if AUTH_TOKEN == "":
        return True
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

@app.get("/rate", dependencies=[Depends(verify_bearer_token)])
def get_rate():
    global cache
    scores = cache.get_song_rates()
    res = RankResponse(ranks=scores)
    return res

@app.post("/rate", dependencies=[Depends(verify_bearer_token)])
def rate_up(data: RateRequest):
    global cache
    cache.vote(data.better_song, data.worse_song)
    res = RateUpResponse(response=f"{data.better_song} > {data.worse_song}")
    return res

@app.get("/rate/{song}", dependencies=[Depends(verify_bearer_token)])
def get_rates(song: str):
    global cache
    song_id = cache.db.get_id_by_song_name(song)
    if not cache.rates.is_node_exist(song_id):
        raise HTTPException(status_code=404, detail="No song with that name were found")
    graph_rank = cache.get_graph_rank_of(song)
    elo_rank = cache.get_elo_rank_of(song)
    elo_score = cache.elo_ranking.scores[song]
    nb_upvotes = cache.rates.get_number_of_upvotes(song_id)
    nb_downvotes = cache.rates.get_number_of_downvotes(song_id)
    certitude = get_certitude(nb_upvotes + nb_downvotes, len(cache.rates))
    res = SongInfoResponse(graph_rank=graph_rank, elo_rank=elo_rank, elo_score=elo_score, nb_upvotes=nb_upvotes, nb_downvotes=nb_downvotes, certitude=certitude)
    return res

@app.post("/status", dependencies=[Depends(verify_bearer_token)])
def status(data: StatusRequest):
    global cache
    first_song_id = cache.db.get_id_by_song_name(data.first_song)
    second_song_id = cache.db.get_id_by_song_name(data.second_song)
    res = get_status_between_songs(cache.rates, first_song_id, second_song_id)
    return res

@app.get("/elo", dependencies=[Depends(verify_bearer_token)])
def get_elo():
    global cache
    scores = cache.get_elo_scores()
    res = RankResponse(ranks=scores)
    return res

@app.get("/artist", dependencies=[Depends(verify_bearer_token)])
def get_artist_rate():
    global cache
    scores = cache.get_artist_rates()
    res = RankResponse(ranks=scores)
    return res
