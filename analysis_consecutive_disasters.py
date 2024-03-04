###
# This file analysis the preprocessed EMDAT data

# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# %% Constants
PATH = "data/df_compound_consecutive_events.csv"

# %%
df = pd.read_csv(PATH, sep=";")

# %% Check if first damages and losses are similar to second damages and losses
df1 = df.loc[
    :,
    ["Hazard 1", "Total Deaths 1", "Total Affected 1", "Total Damages 1", "Type Event"],
].dropna(how="all", subset=["Total Deaths 1", "Total Affected 1", "Total Damages 1"])
df1["Event"] = "First"
df1 = df1.rename(
    columns={
        "Hazard 1": "Hazard",
        "Total Deaths 1": "Total Deaths",
        "Total Affected 1": "Total Affected",
        "Total Damages 1": "Total Damages",
    }
)
df2 = df.loc[
    :,
    ["Hazard 2", "Total Deaths 2", "Total Affected 2", "Total Damages 2", "Type Event"],
].dropna(how="all", subset=["Total Deaths 2", "Total Affected 2", "Total Damages 2"])
df2["Event"] = "Second"
df2 = df2.rename(
    columns={
        "Hazard 2": "Hazard",
        "Total Deaths 2": "Total Deaths",
        "Total Affected 2": "Total Affected",
        "Total Damages 2": "Total Damages",
    }
)
df12 = pd.concat([df1, df2]).reset_index()


# %% Data availability

df12[["Hazard", "Event"]].value_counts().sort_index()


# %%
hazards = ["fl", "ew"]
impacts = [
    "Total Deaths",
    "Total Affected",
    "Total Damages",
]

# %%
fig, axs = plt.subplots(
    2,
    3,
    figsize=(12, 12),
)

i = -1

for hazard in hazards[0:9]:
    hazard_filter = df12.loc[:, "Hazard"] == hazard
    for impact in impacts:
        if hazard == "ew":
            if impact == "Total Damages":
                continue

        i = i + 1
        if sum(hazard_filter) > 0:
            try:
                ax = axs.reshape(-1)[i]
                sns.boxplot(
                    x="Event",
                    y=impact,
                    data=df12[hazard_filter],
                    showfliers=False,
                    showmeans=True,
                    ax=ax,
                    meanprops={
                        # "marker": "s",
                        "markerfacecolor": "red",
                        "markeredgecolor": "red",
                    },
                ).set(title=hazard)
                ax.grid()
                ax.set_xticklabels(ax.get_xticklabels())
            except:
                foo = 2

fig.tight_layout()

# %%
