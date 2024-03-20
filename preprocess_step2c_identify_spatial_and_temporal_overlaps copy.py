# %% Imports
import pandas as pd
import networkx as nx

FIRST_YEAR = 2000
LAST_YEAR = 2018
PROCESSED_IMPACT_PATH_CSV = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df_emdat["Start Date"] = pd.to_datetime(df_emdat["Start Date"])
df_emdat["End Date"] = pd.to_datetime(df_emdat["End Date"])
# %%
df = pd.read_csv("data/event_pairs_50percent.csv", sep=";")

# %% List of event pairs
list_of_tuples = list(
    df.loc[:, ["Event1", "Event2"]].itertuples(index=False, name=None)
)
list_of_lists = [list(ele) for ele in list_of_tuples]

# %%
G = nx.Graph()
# Add nodes to Graph
G.add_nodes_from(sum(list_of_lists, []))
# Create edges from list of nodes
q = [[(s[i], s[i + 1]) for i in range(len(s) - 1)] for s in list_of_lists]
for i in q:
    # Add edges to Graph
    G.add_edges_from(i)


# %%
# Find all connnected components in graph and list nodes for each component
independent_sequences = [sorted(list(i)) for i in nx.connected_components(G)]
unique_events_in_independent_sequences = list(
    set(x for l in independent_sequences for x in l)
)

# %%
# sort sublists in time

# split according to time_lag

# save as 1 df with time_lag column
