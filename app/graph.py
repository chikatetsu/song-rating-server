from json import load as json_load, dump as json_dump


class Graph:
    def __init__(self):
        self._adjacency_list = {}

    def create_edge(self, better_song, worse_song) -> bool:
        is_vote_done = False
        if better_song not in self._adjacency_list:
            self._adjacency_list[better_song] = []
        if worse_song not in self._adjacency_list[better_song]:
            self._adjacency_list[better_song].append(worse_song)
            is_vote_done = True
        if worse_song not in self._adjacency_list:
            self._adjacency_list[worse_song] = []
        elif better_song in self._adjacency_list[worse_song]:
            self._adjacency_list.pop(better_song)
        return is_vote_done

    def load_graph_from_file(self):
        with open("rates_graph.json", "r", encoding="utf-8") as f:
            self._adjacency_list = json_load(f)

    def save_graph(self):
        with open("rates_graph.json", "w", encoding="utf-8") as f:
            json_dump(self._adjacency_list, f, ensure_ascii=False)

    def __len__(self):
        return len(self._adjacency_list)

    def __getitem__(self, item):
        return self._adjacency_list[item]

    def keys(self):
        return self._adjacency_list.keys()

    def values(self):
        return self._adjacency_list.values()

    def items(self):
        return self._adjacency_list.items()

    def is_node_exist(self, node):
        res = node in self._adjacency_list
        return res

    def get_scc(self):
        """ Tarjan pour trouver les SCC """
        index = 0
        indices = {}
        lowlink = {}
        stack = []
        result = []

        def strongconnect(node):
            nonlocal index
            indices[node] = index
            lowlink[node] = index
            index += 1
            stack.append(node)

            for neigh in self._adjacency_list.get(node, []):
                if neigh not in indices:
                    strongconnect(neigh)
                    lowlink[node] = min(lowlink[node], lowlink[neigh])
                elif neigh in stack:
                    lowlink[node] = min(lowlink[node], indices[neigh])

            # si node est une racine de SCC
            if lowlink[node] == indices[node]:
                scc = []
                while True:
                    w = stack.pop()
                    scc.append(w)
                    if w == node:
                        break
                result.append(scc)

        for node in self._adjacency_list:
            if node not in indices:
                strongconnect(node)

        return result

    def condense(self):
        """ Condense le graphe en SCC """
        scc = self.get_scc()
        comp_index = {}
        for i, comp in enumerate(scc):
            for node in comp:
                comp_index[node] = i

        condensed = {i: set() for i in range(len(scc))}

        for u in self._adjacency_list:
            for v in self._adjacency_list[u]:
                cu, cv = comp_index[u], comp_index[v]
                if cu != cv:
                    condensed[cu].add(cv)

        return condensed, scc

def topological_sort(graph):
    visited = {}

    def get_deepness(node):
        if node in visited:
            return visited[node]
        if graph[node] == []:
            visited[node] = 0
            return 0
        max_deepness = 0
        for n in graph[node]:
            deepness = get_deepness(n) + 1
            if deepness > max_deepness:
                max_deepness = deepness
        visited[node] = max_deepness
        return max_deepness

    for node in graph:
        if node not in visited:
            get_deepness(node)

    return sorted(visited, key=visited.get, reverse=True)

def sort_graph(compressed, scc):
    order = topological_sort(compressed)
    rates = []
    for i in order:
        val = scc[i]
        if isinstance(val, list):
            rates.extend(val)
        else:
            rates.append(val)
    return rates
