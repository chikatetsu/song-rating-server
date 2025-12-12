from json import load as json_load
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from collections import defaultdict

from pygments.styles.dracula import background


def load_graph():
    with open("rates_graph.json") as f:
        data = json_load(f)

    graph = nx.DiGraph()
    for parent, enfants in data.items():
        for e in enfants:
            graph.add_edge(parent, e)
    return graph


def descendants_count(graph, node):
    """ Compte le nombre de descendants pour un noeud """
    return len(nx.descendants(graph, node))


def keep_longer_edges(graph):
    H = graph.copy()
    for u in graph.nodes():
        children = list(graph.successors(u))
        if len(children) <= 1:
            continue

        visited = []
        best_score = 0
        for c in children:
            current_score = descendants_count(graph, c)
            if current_score > best_score:
                best_score = current_score
                for v in visited:
                    H.remove_edge(u, v)
                visited = [c]
            elif current_score == best_score:
                visited.append(c)
            else:
                H.remove_edge(u, c)

    return H


def layout_components(graph):
    # Chaque composante faible devient un petit îlot autonome
    components = list(nx.weakly_connected_components(graph))

    pos = {}
    offset_x = 0

    for comp in components:
        sub = graph.subgraph(comp)

        # Mise en page interne
        sub_pos = graphviz_layout(sub, prog="dot", args="-Gnodesep=1.3 -Granksep=1.2")

        # Décale toute la composante pour lui donner son propre espace
        for n, (x, y) in sub_pos.items():
            pos[n] = (x + offset_x, y)

        # On décale le prochain îlot
        offset_x += max(x for (x, y) in sub_pos.values()) + 200  # espace large

    return pos


def simple_layered_layout(graph):
    # Regrouper par profondeur
    layers = defaultdict(list)
    for n in graph.nodes:
        layers[graph.nodes[n]["subset"]].append(n)

    pos = {}
    x_offset = 0

    for depth, nodes in sorted(layers.items(), reverse=True):
        for i, n in enumerate(nodes):
            pos[n] = (i + x_offset, depth)
        x_offset += len(nodes) + 3  # espacement horizontal

    return pos


if __name__ == "__main__":
    G = load_graph()
    G = keep_longer_edges(G)

    # Calculer et stocker le nombre de descendants comme attribut
    for n in G.nodes:
        G.nodes[n]["subset"] = len(nx.descendants(G, n))

    # Calculer la disposition de base (gauche à droite)
    pos = layout_components(G)
    pos = {n: (x * 5, y) for n, (x, y) in pos.items()}

    # Affichage
    plt.figure(figsize=(16, 9))
    nx.draw(
        G,
        pos,
        with_labels=True,
        font_size=6,
        font_family="Noto Sans CJK",
        node_color="lightblue",
        node_size=500,
        linewidths=0.5,
        edgecolors="black",
    )
    plt.title("Arbre trié par nombre de descendants (haut → bas)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()
