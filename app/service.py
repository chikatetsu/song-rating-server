from re import split as re_split

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

def sort_dict_by_score(scores: dict[str, float], reverse = True) -> list[dict[str, object]]:
    sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=reverse)
    res = [{"name": key, "score": value} for key, value in sorted_items]
    return res

def get_certitude(nb_votes: int, nb_songs: int) -> float:
    portion = nb_votes / nb_songs
    cert = 1 - (1 - portion) ** 7
    percentage = round(cert * 100, 2)
    return percentage

def get_status_between_songs(graph: Graph, first_song_id: int, second_song_id: int) -> dict[str, str]:
    is_first_song_exists = graph.is_node_exist(first_song_id)
    is_second_song_exists = graph.is_node_exist(second_song_id)

    if not is_first_song_exists and not is_second_song_exists:
        response = {
            "song": "both",
            "status": "not found"
        }
    elif not is_first_song_exists:
        response = {
            "song": graph[first_song_id].name,
            "status": "not found"
        }
    elif not is_second_song_exists:
        response = {
            "song": graph[second_song_id].name,
            "status": "not found"
        }
    elif first_song_id in graph[second_song_id].worse_songs:
        response = {
            "song": graph[second_song_id].name,
            "status": "better"
        }
    elif second_song_id in graph[first_song_id].worse_songs:
        response = {
            "song": graph[first_song_id].name,
            "status": "better"
        }
    else:
        response = {
            "song": "both",
            "status": "not compared yet"
        }
    return response
