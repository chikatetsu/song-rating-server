from app.db_connection import DBConnection
from app.elo_ranking import EloRanking
from app.graph import Graph
from app.service import sort_dict_by_score, artist_rate


class Cache:
    def __init__(self):
        self.rates = []
        self._is_up_to_date = False

    def _set_rate(self, new_rates):
        self.rates = new_rates

    def update_rates(self, new_rates):
        if not self._is_up_to_date:
            self._set_rate(new_rates)
            self._is_up_to_date = True

    def set_has_outdated(self):
        self._is_up_to_date = False

    def __getitem__(self, item):
        return self.rates[item]


class SongRateCache(Cache):
    def _set_rate(self, new_rates: Graph):
        scores = new_rates.sort_graph()
        self.rates = sort_dict_by_score(scores)

class ArtistRateCache(Cache):
    def _set_rate(self, new_rates: dict[str, float]):
        self.rates = sort_dict_by_score(artist_rate(new_rates))

class EloRatesCache(Cache):
    def _set_rate(self, new_rates: dict[str, float]):
        self.rates = sort_dict_by_score(new_rates)


class RatesCache:
    def __init__(self):
        self.db = DBConnection()
        self.rates = self.db.load_graph()
        self.elo_ranking = EloRanking()
        self._song_rates = SongRateCache()
        self._artist_rates = ArtistRateCache()
        self._elo_rates = EloRatesCache()

    def vote(self, better_song: str, worse_song: str):
        self.db.insert_song(better_song)
        self.db.insert_song(worse_song)
        better_id = self.db.get_id_by_song_name(better_song)
        worse_id = self.db.get_id_by_song_name(worse_song)
        if self.rates.create_edge(better_id, worse_id):
            self.elo_ranking.update_elo(better_song, worse_song)
            self.db.insert_vote(better_id, worse_id)
            self.notify_change()

    def get_song_rates(self) -> list[dict[str, object]]:
        self._song_rates.update_rates(self.rates)
        return self._song_rates.rates

    def get_graph_rank_of(self, song_name: str) -> int:
        self._song_rates.update_rates(self.rates)
        index = 0
        for i in range(len(self.rates)):
            if self._song_rates[i].get("name") == song_name:
                index = i
                break
        return index

    def get_artist_rates(self) -> list[dict[str, object]]:
        self._artist_rates.update_rates(self.elo_ranking.scores)
        return self._artist_rates.rates

    def get_elo_scores(self) -> list[dict[str, object]]:
        self._elo_rates.update_rates(self.elo_ranking.scores)
        return self._elo_rates.rates

    def get_elo_rank_of(self, song_name: str) -> int:
        self._elo_rates.update_rates(self.elo_ranking.scores)
        index = 0
        for i in range(len(self.rates)):
            if self._elo_rates[i].get("name") == song_name:
                index = i
                break
        return index

    def notify_change(self):
        self._song_rates.set_has_outdated()
        self._artist_rates.set_has_outdated()
        self._elo_rates.set_has_outdated()
