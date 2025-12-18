class MusicNode:
    def __init__(self):
        self.name = ""
        self.better_songs: set[int] = set()
        self.worse_songs: set[int] = set()


class Graph:
    def __init__(self):
        self._adjacency_list: dict[int, MusicNode] = {}

    def create_edge(self, better_song: int, worse_song: int) -> bool:
        is_vote_done = False
        if better_song not in self._adjacency_list:
            self._adjacency_list[better_song] = MusicNode()
        if worse_song not in self._adjacency_list:
            self._adjacency_list[worse_song] = MusicNode()

        if worse_song not in self._adjacency_list[better_song].worse_songs:
            self._adjacency_list[better_song].worse_songs.add(worse_song)
            is_vote_done = True
        if better_song not in self._adjacency_list[worse_song].better_songs:
            self._adjacency_list[worse_song].better_songs.add(better_song)
            is_vote_done = True

        if better_song in self._adjacency_list[worse_song].worse_songs:
            self._adjacency_list[worse_song].worse_songs.remove(better_song)
        if worse_song in self._adjacency_list[better_song].better_songs:
            self._adjacency_list[better_song].better_songs.remove(worse_song)

        return is_vote_done

    def __len__(self):
        return len(self._adjacency_list)

    def __getitem__(self, item: int) -> MusicNode:
        return self._adjacency_list[item]

    def keys(self):
        return self._adjacency_list.keys()

    def values(self):
        return self._adjacency_list.values()

    def items(self):
        return self._adjacency_list.items()

    def is_node_exist(self, node: int) -> bool:
        res = node in self._adjacency_list
        return res

    def rename_node(self, node_id: int, node_name: str):
        if node_id in self._adjacency_list:
            self._adjacency_list[node_id].name = node_name

    def get_name(self, index: int) -> str:
        res = self._adjacency_list.get(index, MusicNode()).name
        return res

    def get_number_of_upvotes(self, song_id: int) -> int:
        if self.is_node_exist(song_id):
            nb_votes = len(self._adjacency_list[song_id].worse_songs)
            return nb_votes
        return 0

    def get_number_of_downvotes(self, song_id: int) -> int:
        if self.is_node_exist(song_id):
            nb_votes = len(self._adjacency_list[song_id].better_songs)
            return nb_votes
        return 0

    def sort_graph(self) -> dict[str, float]:
        if not self._adjacency_list: # if empty
            return {}
        deepnesses = self.map_deepness()
        rates: dict[str, float] = {}
        votes: dict[int, tuple[int, int]] = {}

        max_upvotes = 0
        max_downvotes = 0
        for song_id in deepnesses.keys():
            current_upvotes = self.get_number_of_upvotes(song_id)
            current_downvotes = self.get_number_of_downvotes(song_id)
            votes[song_id] = (current_upvotes, current_downvotes)
            if current_upvotes > max_upvotes:
                max_upvotes = current_upvotes
            if current_downvotes > max_downvotes:
                max_downvotes = current_downvotes

        for song_index, nb_vote in votes.items():
            score = deepnesses[song_index]
            if max_upvotes > 0:
                score += (nb_vote[0] / max_upvotes)
            if max_downvotes > 0:
                score -= (nb_vote[1] / max_downvotes)
            rates[self.get_name(song_index)] = score

        return rates


    def map_deepness(self) -> dict[int, int]:
        visited: dict[int, int] = {}
        visiting = set()

        def get_deepness(node_id: int):
            if node_id in visited:
                return visited[node_id]
            if node_id in visiting:
                return 0
            if not self._adjacency_list[node_id]:
                visited[node_id] = 0
                return 0

            visiting.add(node_id)

            max_deepness = 0
            for n in self._adjacency_list[node_id].worse_songs:
                deepness = get_deepness(n) + 1
                max_deepness = max(max_deepness, deepness)

            visiting.remove(node_id)
            visited[node_id] = max_deepness
            return max_deepness

        for song_id in self._adjacency_list.keys():
            if song_id not in visited:
                get_deepness(song_id)
        return visited
