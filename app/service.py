from re import split as re_split

from app.dto import StatusBetweenSongsResponse, RankObject
from app.graph import Graph


def artist_rate(elo: dict[str, float]) -> dict[str, float]:
    artists = {}
    formatted_elo = {song.replace("Tyler, The Creator", "Tyler The Creator"): score for song, score in elo.items()}
    songs = list(formatted_elo.keys())

    for current_song in songs:
        unformatted_artists = current_song.split(" - ")[-1]
        song_artists = re_split(r'\s*(?:, |&)\s*', unformatted_artists)

        for current_artist in song_artists:
            if current_artist in artists:
                continue

            scores = []
            for song in songs:
                if current_artist in song:
                    scores.append(formatted_elo[song])
            artists[current_artist] = sum(scores) / len(scores)

    return artists

def sort_dict_by_score(scores: dict[str, float], reverse = True) -> list[RankObject]:
    sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=reverse)
    res = [RankObject(name=key, score=value, old_rank=i + 1) for i, (key, value) in enumerate(sorted_items)]
    return res

def to_rank_only(ranks: list[RankObject]) -> dict[str, int]:
    rank_dict = {}
    for i in range(len(ranks)):
        rank_dict[ranks[i].name] = i + 1
    return rank_dict

def get_certitude(nb_votes: int, nb_songs: int) -> float:
    portion = nb_votes / nb_songs
    cert = 1 - (1 - portion) ** 7
    percentage = round(cert * 100, 2)
    return percentage

def get_status_between_songs(graph: Graph, first_song_id: int, second_song_id: int) -> StatusBetweenSongsResponse:
    first_song = graph[first_song_id]
    second_song = graph[second_song_id]
    if first_song is None:
        return None
    if second_song is None:
        return None
    if first_song_id in second_song.worse_songs:
        response = StatusBetweenSongsResponse(message=f"{second_song.name} > {first_song.name}", is_compared=True)
    elif second_song_id in first_song.worse_songs:
        response = StatusBetweenSongsResponse(message=f"{first_song.name} > {second_song.name}", is_compared=True)
    else:
        response = StatusBetweenSongsResponse(message=f"{first_song.name} et {second_song.name} n'ont jamais été comparé", is_compared=False)
    return response

def get_next_song(graph: Graph, song_id: int) -> str | None:
    current_song = graph[song_id]
    if current_song is None:
        return None
    for i in current_song.better_songs:
        if graph[i] is None:
            current_song.better_songs.remove(i)
            continue
        for j in graph[i].worse_songs:
            if j == song_id:
                continue
            if j in current_song.better_songs:
                continue
            if j in current_song.worse_songs:
                continue
            if graph[j] is None:
                graph[i].worse_songs.remove(j)
                continue
            if graph[j].name == "":
                graph[i].worse_songs.remove(j)
                continue
            return graph[j].name

    for i in current_song.worse_songs:
        if graph[i] is None:
            current_song.worse_songs.remove(i)
            continue
        for j in graph[i].better_songs:
            if j == song_id:
                continue
            if j in current_song.better_songs:
                continue
            if j in current_song.worse_songs:
                continue
            if graph[j] is None:
                graph[i].better_songs.remove(j)
                continue
            if graph[j].name == "":
                graph[i].better_songs.remove(j)
                continue
            return graph[j].name
    return None
