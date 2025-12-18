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
        res = self._adjacency_list.get(index, MusicNode).name
        return res

    def get_scc(self) -> list[list[str]]:
        """ Tarjan pour trouver les SCC """
        index = 0
        indices: dict[int, int] = {}
        lowlink: dict[int, int] = {}
        stack: list[int] = []
        result: list[list[str]] = []

        def strongconnect(node: int):
            nonlocal index
            indices[node] = index
            lowlink[node] = index
            index += 1
            stack.append(node)

            for neigh in self._adjacency_list.get(node, MusicNode()).worse_songs:
                if neigh not in indices:
                    strongconnect(neigh)
                    lowlink[node] = min(lowlink[node], lowlink[neigh])
                elif neigh in stack:
                    lowlink[node] = min(lowlink[node], indices[neigh])

            # si node est une racine de SCC
            if lowlink[node] == indices[node]:
                scc: list[str] = []
                while True:
                    w = stack.pop()
                    scc.append(self.get_name(w))
                    if w == node:
                        break
                result.append(scc)

        for n in self._adjacency_list:
            if n not in indices:
                strongconnect(n)

        return result

    def condense(self, scc: list[list[str]]) -> dict[int, set[int]]:
        """ Condense le graphe en SCC """
        comp_index: dict[str, int] = {}
        for i, comp in enumerate(scc):
            for node in comp:
                comp_index[node] = i

        condensed = {i: set() for i in range(len(scc))}

        for u in self._adjacency_list:
            u_name = self.get_name(u)
            for v in self._adjacency_list[u].worse_songs:
                v_name = self.get_name(v)
                cu, cv = comp_index[u_name], comp_index[v_name]
                if cu != cv:
                    condensed[cu].add(cv)

        return condensed


def map_deepness(graph: dict[int, set[int]]) -> list[int]:
    visited: dict[int, int] = {}

    def get_deepness(node_id: int):
        if node_id in visited:
            return visited[node_id]
        if not graph[node_id]: # if empty
            visited[node_id] = 0
            return 0
        max_deepness = 0
        for n in graph[node_id]:
            deepness = get_deepness(n) + 1
            if deepness > max_deepness:
                max_deepness = deepness
        visited[node_id] = max_deepness
        return max_deepness

    for song_id in graph.keys():
        if song_id not in visited:
            get_deepness(song_id)

    res = sorted(visited, key=visited.get, reverse=True) #TODO: REMOVE IMPORTANT HERE LOOK AT ME BITCH
    return res


def sort_graph(compressed: dict[int, set[int]], scc: list[list[str]]):
    order = map_deepness(compressed)

    rates = []
    for i in order:
        val = scc[i]
        if isinstance(val, list):
            rates.extend(val)
        else:
            rates.append(val)
    return rates
