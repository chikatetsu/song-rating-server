from elo_ranking import EloRanking
from graph import Graph, sort_graph
from service import sort_dict_by_score, artist_rate


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
    def _set_rate(self, new_rates):
        compressed, scc = new_rates.condense()
        self.rates = sort_graph(compressed, scc)

class ArtistRateCache(Cache):
    def _set_rate(self, new_rates):
        self.rates = sort_dict_by_score(artist_rate(new_rates))

class EloRatesCache(Cache):
    def _set_rate(self, new_rates):
        self.rates = sort_dict_by_score(new_rates)


class RatesCache:
    def __init__(self):
        self.rates = Graph()
        self.rates.load_graph_from_file()
        self.elo_ranking = EloRanking()
        self._song_rates = SongRateCache()
        self._artist_rates = ArtistRateCache()
        self._elo_rates = EloRatesCache()

    def get_song_rates(self) -> list[str]:
        self._song_rates.update_rates(self.rates)
        return self._song_rates.rates

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
