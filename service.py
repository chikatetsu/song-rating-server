from graph import Graph
from re import split as re_split


def artist_rate(elo: dict[str, float]) -> dict[str, float]:
    artists = {}
    formatted_elo = {song.replace("Tyler, The Creator", "Tyler The Creator"): artist for song, artist in elo.items()}
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

def sort_dict_by_score(scores: dict[str, float], reverse = True) -> list[dict[str, object]]:
    sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=reverse)
    res = [{"name": key, "score": value} for key, value in sorted_items]
    return res

def get_number_of_upvotes(graph: Graph, song: str) -> int:
    if graph.is_node_exist(song):
        nb_votes = len(graph[song])
        return nb_votes
    return 0

def get_number_of_downvotes(graph: Graph, song: str) -> int:
    nb_votes = 0
    for votes in graph.values():
        if song in votes:
            nb_votes += 1
    return nb_votes

def get_certitude(nb_votes: int, nb_songs: int) -> float:
    portion = nb_votes / nb_songs
    cert = 1 - (1 - portion) ** 7
    percentage = round(cert * 100, 2)
    return percentage

def get_status_between_songs(graph: Graph, song1: str, song2: str) -> dict[str, str]:
    is_first_song_exists = graph.is_node_exist(song1)
    is_second_song_exists = graph.is_node_exist(song2)

    if not is_first_song_exists and not is_second_song_exists:
        response = {
            "song": "both",
            "status": "not found"
        }
    elif not is_first_song_exists:
        response = {
            "song": song1,
            "status": "not found"
        }
    elif not is_second_song_exists:
        response = {
            "song": song2,
            "status": "not found"
        }
    elif song1 in graph[song2]:
        response = {
            "song": song2,
            "status": "better"
        }
    elif song2 in graph[song1]:
        response = {
            "song": song1,
            "status": "better"
        }
    else:
        response = {
            "song": "both",
            "status": "not compared yet"
        }
    return response
