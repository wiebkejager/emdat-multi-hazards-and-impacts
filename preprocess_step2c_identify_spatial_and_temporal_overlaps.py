# %% Imports
import pandas as pd
import networkx as nx
import json


# %%
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
list_of_event_pair_tuples = list(
    df.loc[:, ["Event1", "Event2"]].itertuples(index=False, name=None)
)
list_of_event_pair_lists = [list(ele) for ele in list_of_event_pair_tuples]

# %%
G = nx.Graph()
# Add nodes to Graph
G.add_nodes_from(sum(list_of_event_pair_lists, []))
# Create edges from list of nodes
q = [[(s[i], s[i + 1]) for i in range(len(s) - 1)] for s in list_of_event_pair_lists]
for i in q:
    # Add edges to Graph
    G.add_edges_from(i)

# %%
# Find all connnected components in graph and list nodes for each component
list_of_independent_sequence_lists = [
    sorted(list(i)) for i in nx.connected_components(G)
]
unique_events_in_independent_sequences = list(
    set(x for l in list_of_independent_sequence_lists for x in l)
)

# %%
# sort sublists in time
list_of_independent_sequence_lists_dated = [
    sorted([tuple([i, df_emdat.loc[i, "Start Date"]]) for i in seq], key=lambda a: a[1])
    for seq in list_of_independent_sequence_lists
]

# %% Add single events to list
single_events_filter = [
    ix not in unique_events_in_independent_sequences for ix in df_emdat.index
]
list_of_single_event_dated = [
    [x]
    for x in list(
        df_emdat.reset_index()
        .loc[single_events_filter, ["Dis No", "Start Date"]]
        .itertuples(index=False, name=None)
    )
]


# %%
def split_at_timelag(l, TIME_LAG):
    # return a list of list split at time_lags
    indices = []
    first_index = 0
    last_index = len(l)
    for i in range(1, len(l)):
        time_diff = (l[i][1] - l[i - 1][1]).days
        if time_diff > TIME_LAG:
            indices.append([first_index, i - 1])
            first_index = i

    indices.append([first_index, last_index])
    return [l[s : e + 1] for s, e in indices]


# %% split according to time_lag
df = pd.DataFrame()
TIME_LAGS = [0, 91, 182, 365, 6935]

for TIME_LAG in TIME_LAGS:
    # split lists at timelag
    list_of_independent_sequence_lists_dated_split = [
        split_at_timelag(l, TIME_LAG) for l in list_of_independent_sequence_lists_dated
    ]

    # flatten list 1 level
    list_of_independent_sequence_lists_dated_split = [
        x for xs in list_of_independent_sequence_lists_dated_split for x in xs
    ]

    # add single events
    list_of_independent_sequence_lists_dated_split = (
        list_of_independent_sequence_lists_dated_split + list_of_single_event_dated
    )

    # remove date and convert list to string
    list_of_independent_sequence_lists_split = [
        json.dumps([e[0] for e in l])
        for l in list_of_independent_sequence_lists_dated_split
    ]

    # add to dataframe with timelag info
    dict = {
        "Events": list_of_independent_sequence_lists_split,
        "Timelag": TIME_LAG,
    }
    df = pd.concat([df, pd.DataFrame(dict)], ignore_index=True)


# %% Save
df.to_csv("data/df_s_t_overlapping_events.csv", sep=";")

# %%
