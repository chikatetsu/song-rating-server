import json
import networkx as nx
import matplotlib.pyplot as plt

# Charger le graphe depuis le JSON
with open("rates_graph.json") as f:
    data = json.load(f)

# Construire le graphe orienté
G = nx.DiGraph()
for parent, enfants in data.items():
    for e in enfants:
        G.add_edge(parent, e)

# Fonction pour compter le nombre de descendants
def count_descendants(node):
    return len(nx.descendants(G, node))

# Calculer et stocker le nombre de descendants comme attribut
for n in G.nodes:
    G.nodes[n]["subset"] = count_descendants(n)

# Calculer la disposition de base (gauche à droite)
pos = nx.multipartite_layout(G, subset_key="subset")

# 🔄 Rotation du graphe pour que ça aille de haut en bas
pos = {node: (y, -x) for node, (x, y) in pos.items()}

# Affichage
plt.figure(figsize=(10, 8))
nx.draw(
    G,
    pos,
    with_labels=True,
    node_color="lightblue",
    node_size=2500,
    font_size=9,
    font_weight="bold",
    arrows=True,
)
plt.title("Arbre trié par nombre de descendants (haut → bas)")
plt.axis("off")
plt.tight_layout()
plt.show()
