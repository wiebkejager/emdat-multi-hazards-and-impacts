###
# This file analysis the preprocessed EMDAT data

# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import missingno as msno

from my_functions import get_bs_sample_df, get_impact_mean

# %% Constants
PATH = "data/df_impacts_of_single_and_pair_events.csv"

# %%
df = pd.read_csv(PATH, sep=";")

# %% Check if first damages and losses are similar to second damages and losses
df1 = df.loc[
    :, ["Hazard 1", "Total Deaths 1", "Total Affected 1", "Total Damages 1"]
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
    :, ["Hazard 2", "Total Deaths 2", "Total Affected 2", "Total Damages 2"]
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
hazards = df12["Hazard"].unique()
impacts = [
    "Total Damages",
    "Total Affected",
    "Total Deaths",
]

# %%
fig, axs = plt.subplots(
    9,
    3,
    figsize=(12, 24),
    # width_ratios=[3, 3, 3],
)

i = -1

for hazard in hazards[0:9]:
    hazard_filter = df12.loc[:, "Hazard"] == hazard
    for impact in impacts:
        i = i + 1
        if sum(hazard_filter) > 0:
            try:
                ax = axs.reshape(-1)[i]
                sns.boxplot(
                    x="Event",
                    y=impact,
                    data=df12[hazard_filter],
                    showfliers=False,
                    showmeans=False,
                    ax=ax,
                    meanprops={
                        # "marker": "s",
                        "markerfacecolor": "black",
                        "markeredgecolor": "black",
                    },
                ).set(title=hazard)
                ax.grid()
                ax.set_xticklabels(ax.get_xticklabels())
            except:
                foo = 2

fig.tight_layout()

# %%
