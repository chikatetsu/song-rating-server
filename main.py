from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from os import getenv

from dto import RateRequest, StatusRequest, RateUpResponse, RankResponse, SongInfoResponse
from rates_cache import RatesCache
from service import get_certitude, get_number_of_downvotes, get_number_of_upvotes, get_status_between_songs


load_dotenv()
AUTH_TOKEN = getenv("AUTH_TOKEN")

app = FastAPI()
security = HTTPBearer()
cache = RatesCache()

def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

@app.post("/rate", dependencies=[Depends(verify_bearer_token)])
def rate_up(data: RateRequest):
    global cache
    if cache.rates.create_edge(data.better_song, data.worse_song):
        cache.elo_ranking.update_elo(data.better_song, data.worse_song)
        cache.rates.save_graph()
        cache.notify_change()
    res = RateUpResponse(response=f"{data.better_song} > {data.worse_song}")
    return res

@app.post("/status", dependencies=[Depends(verify_bearer_token)])
def status(data: StatusRequest):
    global cache
    res = get_status_between_songs(cache.rates, data.first_song, data.second_song)
    return res

@app.get("/rate", dependencies=[Depends(verify_bearer_token)])
def get_rate():
    global cache
    scores = cache.get_song_rates()
    res = RankResponse(ranks=scores)
    return res

@app.get("/elo", dependencies=[Depends(verify_bearer_token)])
def get_elo():
    global cache
    scores = cache.get_elo_scores()
    res = RankResponse(ranks=scores)
    return res

@app.get("/rate/{song}", dependencies=[Depends(verify_bearer_token)])
def get_rates(song: str):
    global cache
    if not cache.rates.is_node_exist(song):
        raise HTTPException(status_code=404, detail="No song with that name were found")
    graph_rates = cache.get_song_rates()
    graph_rank = graph_rates.index(song)
    elo_rank = cache.get_elo_rank_of(song)
    elo_score = cache.elo_ranking.scores[song]
    nb_upvotes = get_number_of_upvotes(cache.rates, song)
    nb_downvotes = get_number_of_downvotes(cache.rates, song)
    certitude = get_certitude(nb_upvotes + nb_downvotes, len(cache.rates))
    res = SongInfoResponse(graph_rank=graph_rank, elo_rank=elo_rank, elo_score=elo_score, nb_upvotes=nb_upvotes, nb_downvotes=nb_downvotes, certitude=certitude)
    return res

@app.get("/artist", dependencies=[Depends(verify_bearer_token)])
def get_artist_rate():
    global cache
    scores = cache.get_artist_rates()
    res = RankResponse(ranks=scores)
    return res
