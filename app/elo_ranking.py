from json import load as json_load, dump as json_dump

from app.graph import Graph


class EloRanking:
    def __init__(self):
        # self.scores = {}
        self.scores = self._load_scores()

    def update_elo(self, winner_name: str, loser_name: str, K=32):
        winner_score = self.scores.get(winner_name, 1000)
        loser_score = self.scores.get(loser_name, 1000)
        expected_winner = 1 / (1 + 10 ** ((loser_score - winner_score) / 400))
        expected_loser = 1 - expected_winner
        winner_score += K * (1 - expected_winner)
        loser_score += K * (0 - expected_loser)
        self.scores[winner_name], self.scores[loser_name] = winner_score, loser_score
        self._save_scores()

    @staticmethod
    def _load_scores() -> dict[str, float]:
        with open("elo_scores.json", "r") as f:
            elo_scores = json_load(f)
        return elo_scores

    def _save_scores(self):
        with open("elo_scores.json", "w") as f:
            json_dump(self.scores, f, ensure_ascii=False)


def init_elo(graph: Graph) -> dict[str, float]:
    remainings = [node.name for node in graph.values()]
    ranking = EloRanking()
    i = 0
    while len(remainings) > 0:
        j = 0
        while j < len(remainings):
            song = remainings[j]
            if len(graph[song].worse_songs) == i:
                remainings.pop(j)
                continue
            other_song = graph[song].worse_songs[i]
            ranking.update_elo(song, other_song)
            j += 1
        i += 1
    return ranking.scores


# if __name__ == '__main__':
#     rates = Graph()
#     rates.load_graph_from_file()
#     scores = sort_dict_by_score(init_elo(rates))
#     for i in range(len(scores)):
#         print(f"{i + 1}. {scores[i][0]}\t{scores[i][1]}")
