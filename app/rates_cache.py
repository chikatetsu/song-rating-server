from datetime import datetime, timedelta

from app.dto import RankObject
from db_connection import DBConnection
from app.elo_ranking import EloRanking
from app.graph import Graph
from app.service import sort_dict_by_score, artist_rate, to_rank_only


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

class OldRankCache(Cache):
    def __init__(self):
        super().__init__()
        self.last_update = datetime.now()

    def _set_rate(self, new_rates: list[RankObject]):
        self.rates = to_rank_only(new_rates)
        self.last_update = datetime.now()


class RatesCache:
    def __init__(self):
        self.db = DBConnection()
        self.rates = self.db.load_graph()
        self.elo_ranking = EloRanking()

        self._song_rates = SongRateCache()
        self._artist_rates = ArtistRateCache()
        self._elo_rates = EloRatesCache()
        self._old_song_rates = OldRankCache()

        self._song_rates.update_rates(self.rates)
        self._old_song_rates.update_rates(self._song_rates.rates)

    def vote(self, better_song: str, worse_song: str):
        self.db.insert_song(better_song)
        self.db.insert_song(worse_song)
        better_id = self.db.get_id_by_song_name(better_song)
        worse_id = self.db.get_id_by_song_name(worse_song)
        if self.rates.create_edge(better_id, worse_id):
            self.elo_ranking.update_elo(better_song, worse_song)
            self.db.insert_vote(better_id, worse_id)
            self.notify_change()

    def get_song_rates(self) -> list[RankObject]:
        self._song_rates.update_rates(self.rates)
        song_rates = self._song_rates.rates
        if self._old_song_rates.last_update + timedelta(days=7) > datetime.now():
            self._old_song_rates.set_has_outdated()
            self._old_song_rates.update_rates(song_rates)
        else:
            for i in range(len(song_rates)):
                song_rates[i].old_rank = self._old_song_rates.rates.get(song_rates[i].name, song_rates[i].score)
        return song_rates

    def get_graph_rank_of(self, song_name: str) -> int:
        self._song_rates.update_rates(self.rates)
        for i in range(len(self.rates)):
            if self._song_rates[i].name == song_name:
                return i
        return -1

    def get_artist_rates(self) -> list[RankObject]:
        self._artist_rates.update_rates(self.elo_ranking.scores)
        return self._artist_rates.rates

    def get_elo_scores(self) -> list[RankObject]:
        self._elo_rates.update_rates(self.elo_ranking.scores)
        return self._elo_rates.rates

    def get_elo_rank_of(self, song_name: str) -> int:
        self._elo_rates.update_rates(self.elo_ranking.scores)
        for i in range(len(self.rates)):
            if self._elo_rates[i].name == song_name:
                return i
        return -1

    def notify_change(self):
        self._song_rates.set_has_outdated()
        self._artist_rates.set_has_outdated()
        self._elo_rates.set_has_outdated()
