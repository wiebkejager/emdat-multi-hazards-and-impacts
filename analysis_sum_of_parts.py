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
df_all = pd.read_csv(PATH, sep=";")

# %%
df1 = df_all.loc[
    :, ["Hazard 1", "Total Deaths 1", "Total Affected 1", "Total Damages 1"]
].dropna(how="all", subset=["Total Deaths 1", "Total Affected 1", "Total Damages 1"])
df1["Event"] = "Single"
df1["Hazard 2"] = np.nan
df1 = df1.rename(
    columns={
        "Total Deaths 1": "Total Deaths",
        "Total Affected 1": "Total Affected",
        "Total Damages 1": "Total Damages",
    }
)
df2 = df_all.loc[
    :,
    [
        "Hazard 1",
        "Hazard 2",
        "Total Deaths 12",
        "Total Affected 12",
        "Total Damages 12",
    ],
].dropna(how="all", subset=["Total Deaths 12", "Total Affected 12", "Total Damages 12"])
df2["Event"] = "Double"
df2 = df2.rename(
    columns={
        "Total Deaths 12": "Total Deaths",
        "Total Affected 12": "Total Affected",
        "Total Damages 12": "Total Damages",
    }
)
df = pd.concat([df1, df2]).reset_index()

# Add column indicating event sequence
df.loc[:, "eventtype_detailed"] = df[["Hazard 1", "Hazard 2"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)  # %%

# %%
event_counts = df.loc[:, "eventtype_detailed"].value_counts()
hazards = sorted(event_counts[event_counts >= 20].index)
# drop triple hazards. we only compare pairs
hazard_pairs = [item for item in hazards if len(item) < 6 and len(item) > 2]

# %%
# %% Compare mean damages: I.e. if and only if Z = X + Y than E(Z) = E(X) + E(Y)
iterables = [
    ["Total Damages", "Total Affected", "Total Deaths"],
    ["whole", "sum", "whole/sum"],
]
index = pd.MultiIndex.from_product(iterables, names=["first", "second"])
df_res = pd.DataFrame(index=index, columns=hazard_pairs)

for hazard_pair in hazard_pairs:
    ## Damages
    # pairs
    df_res.loc[index[0], hazard_pair] = df.loc[
        df.loc[:, "eventtype_detailed"] == hazard_pair, index[0][0]
    ].mean()
    # sum
    [haz1, haz2] = hazard_pair.split(",")
    df_res.loc[index[1], hazard_pair] = (
        df.loc[df.loc[:, "eventtype_detailed"] == haz1, index[0][0]].mean()
        + df.loc[df.loc[:, "eventtype_detailed"] == haz2, index[0][0]].mean()
    )
    # sum/pairs
    df_res.loc[index[2], hazard_pair] = (
        df_res.loc[index[0], hazard_pair] / df_res.loc[index[1], hazard_pair]
    )
    ## Affected
    # pairs
    df_res.loc[index[3], hazard_pair] = df.loc[
        df.loc[:, "eventtype_detailed"] == hazard_pair, index[3][0]
    ].mean()
    # sum
    [haz1, haz2] = hazard_pair.split(",")
    df_res.loc[index[4], hazard_pair] = (
        df.loc[df.loc[:, "eventtype_detailed"] == haz1, index[3][0]].mean()
        + df.loc[df.loc[:, "eventtype_detailed"] == haz2, index[3][0]].mean()
    )
    # sum/pairs
    df_res.loc[index[5], hazard_pair] = (
        df_res.loc[index[3], hazard_pair] / df_res.loc[index[4], hazard_pair]
    )

    ## Deaths
    # pairs
    df_res.loc[index[6], hazard_pair] = df.loc[
        df.loc[:, "eventtype_detailed"] == hazard_pair, index[6][0]
    ].mean()
    # sum
    [haz1, haz2] = hazard_pair.split(",")
    df_res.loc[index[7], hazard_pair] = (
        df.loc[df.loc[:, "eventtype_detailed"] == haz1, index[6][0]].mean()
        + df.loc[df.loc[:, "eventtype_detailed"] == haz2, index[6][0]].mean()
    )
    # sum/pairs
    df_res.loc[index[8], hazard_pair] = (
        df_res.loc[index[6], hazard_pair] / df_res.loc[index[7], hazard_pair]
    )

df_res = df_res.astype("float64").round(1)
df_res.to_csv("data/sum_and_whole_damages.csv", sep=";")


# %%

fig, axs = plt.subplots(
    3,
    3,
    figsize=(12, 12),
    # width_ratios=[3, 3, 3],
)
hazard_groups = [
    ["eq", "ls", "eq,ls"],
    ["eq", "ls", "eq,ls"],
    ["eq", "ls", "eq,ls"],
    ["ew", "fl", "ew,fl"],
    ["ew", "fl", "ew,fl"],
    ["ew", "fl", "ew,fl"],
    ["fl", "ls", "fl,ls"],
    ["fl", "ls", "fl,ls"],
    ["fl", "ls", "fl,ls"],
]
impacts = [
    "Total Damages",
    "Total Affected",
    "Total Deaths",
    "Total Damages",
    "Total Affected",
    "Total Deaths",
    "Total Damages",
    "Total Affected",
    "Total Deaths",
    "Total Damages",
    "Total Affected",
    "Total Deaths",
    "Total Damages",
    "Total Affected",
    "Total Deaths",
    "Total Damages",
    "Total Affected",
    "Total Deaths",
]

i = -1

for ax in axs.reshape(-1):
    i = i + 1
    hazard_group = hazard_groups[i]
    hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_group)
    sns.boxplot(
        x="eventtype_detailed",
        y=impacts[i],
        data=df[hazard_filter],
        ax=ax,
        order=hazard_group,
        showfliers=False,
        showmeans=False,
        meanprops={
            # "marker": "s",
            "markerfacecolor": "black",
            "markeredgecolor": "black",
        },
    ).set(xlabel="Hazard Type")
    # ax.semilogy(base=2)
    ax.grid()
    ax.set_xticklabels(ax.get_xticklabels())

fig.tight_layout()

# %%
df_res_factor = (
    df_res.loc[(slice(None), "whole/sum"), :]
    .reset_index()
    .melt(id_vars=["first", "second"], var_name="event_type", value_name="factor")
    .drop("second", axis=1)
    .rename({"first": "impact_type"}, axis=1)
)


# %% Bootstrap distribution mean damages: I.e. if and only if Z = X + Y than E(Z) = E(X) + E(Y)
cols = ["sample_id", "event_type", "impact_type", "factor"]
df_bs = pd.DataFrame(
    columns=cols,
)

n = 1
N = 1000
impact_vars = ["Total Damages", "Total Affected", "Total Deaths"]

for hazard_pair in hazard_pairs:
    [haz1, haz2] = hazard_pair.split(",")
    for n in range(N):
        df_bs_haz1 = get_bs_sample_df(df, haz1)
        df_bs_haz2 = get_bs_sample_df(df, haz2)
        df_bs_haz12 = get_bs_sample_df(df, hazard_pair)

        for impact_var in impact_vars:
            factor = get_impact_mean(df_bs_haz12, impact_var) / (
                get_impact_mean(df_bs_haz1, impact_var)
                + get_impact_mean(df_bs_haz2, impact_var)
            )
            new_row = pd.DataFrame([[n, hazard_pair, impact_var, factor]], columns=cols)
            df_bs = pd.concat([df_bs, new_row], ignore_index=True)

        n = n + 1

# %%
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
# ax = sns.boxplot(
#     x="event_type",
#     y="factor",
#     data=df_bs,
#     hue="impact_type",
#     showfliers=False,
#     whis=(2.5, 97.5),
# )

ax = sns.pointplot(
    x="event_type",
    y="factor",
    hue="impact_type",
    data=df_bs,
    dodge=0.2,
    join=False,
    errorbar=("pi", 95),
    markers="|",
    legend=False,
)


plt.yscale("log")
ax.axhline(1, 0, 1, color="black")
ax = sns.pointplot(
    x="event_type",
    y="factor",
    hue="impact_type",
    data=df_res_factor,
    dodge=0.2,
    errorbar=("pi", 0),
    join=False,
)
sns.move_legend(
    ax,
    "lower center",
    bbox_to_anchor=(0.5, 1),
    ncol=3,
    title=None,
    frameon=False,
)

ax.yaxis.grid(True)  # Hide the horizontal gridlines
fig.tight_layout()
