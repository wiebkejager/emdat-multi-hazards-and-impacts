# %%
L = [
    ["a", "b", "c"],
    ["b", "d", "e"],
    ["k"],
    ["o", "p"],
    ["e", "f"],
    ["p", "a"],
    ["d", "g"],
    ["k", "fo"],
]

import networkx as nx


G = nx.Graph()

# Add nodes to Graph
G.add_nodes_from(sum(L, []))

# Create edges from list of nodes
q = [[(s[i], s[i + 1]) for i in range(len(s) - 1)] for s in L]

for i in q:

    # Add edges to Graph
    G.add_edges_from(i)

# Find all connnected components in graph and list nodes for each component
[list(i) for i in nx.connected_components(G)]

# %%
