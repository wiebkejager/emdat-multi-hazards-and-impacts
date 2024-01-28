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
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %%
df = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

# %% Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: "multi-hazard" if sum(x.isna()) <= 1 else "single-hazard", axis=1
)
# Add column indicating event sequence
df.loc[:, "eventtype_detailed"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)

# Add column indicating event set alphabetically
df.loc[:, "eventtype_detailed_unsrt"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(list(x.dropna())), axis=1
)

# %% Filter out event types that occurr little
event_counts = df.loc[:, "eventtype_detailed"].value_counts()
hazards = sorted(event_counts[event_counts >= 20].index)
# drop triple hazards. we only compare pairs
hazard_pairs = [item for item in hazards if len(item) < 6 and len(item) > 2]


# %% Compare mean damages: I.e. if and only if Z = X + Y than E(Z) = E(X) + E(Y)
iterables = [
    ["Total Damages, Adjusted ('000 US$')", "Total Affected", "Total Deaths"],
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
df_res.to_csv("associated_damages.csv", sep=";")

# %%
data_indicator = pd.read_csv("data_indicator.csv", sep=";")
data_indicator

# %%
impact_vars = ["Total Damages, Adjusted ('000 US$')", "Total Affected", "Total Deaths"]

# %%
df2 = df.copy(deep=True)
for ix, row in data_indicator.iterrows():
    hazard_filter = df2.loc[:, "eventtype_detailed"].isin([row.event_type])
    for impact_var in impact_vars:
        if row[impact_var] == False:
            df2.loc[hazard_filter, impact_var] = np.nan


# %%
df_res_factor = (
    df_res.loc[(slice(None), "whole/sum"), :]
    .reset_index()
    .melt(id_vars=["first", "second"], var_name="event_type", value_name="factor")
    .drop("second", axis=1)
    .rename({"first": "impact_type"}, axis=1)
)

# %%
cwew_hazards = ["cw", "ew", "cw,ew"]
foo = df2[df2.loc[:, "eventtype_detailed"].isin(cwew_hazards)].dropna(
    subset="Total Deaths"
)

# %%
foo["Duration"] = (
    (
        pd.to_datetime(foo.loc[:, "End Date"])
        - pd.to_datetime(foo.loc[:, "Start Date"])
    ).dt.total_seconds()
    / 60
    / 60
    / 24
)  # in days

# %%
sns.histplot(data=foo, x="Continent", hue="eventtype_detailed", multiple="stack")

# %%
sns.boxplot(
    data=foo,
    y="Dis Mag Value",
    x="eventtype_detailed_unsrt",
    showfliers=False,
)

# %%
sns.boxplot(
    data=foo,
    y="Duration",
    x="eventtype_detailed_unsrt",
    showfliers=False,
)

# %% Boxplots to compare damage distributions

fig, axs = plt.subplots(
    6,
    3,
    figsize=(12, 24),
    # width_ratios=[3, 3, 3],
)
hazard_groups = [
    ["cw", "ew", "cw,ew"],
    ["cw", "ew", "cw,ew"],
    ["cw", "ew", "cw,ew"],
    ["dr", "hw", "dr,hw"],
    ["dr", "hw", "dr,hw"],
    ["dr", "hw", "dr,hw"],
    ["eq", "ls", "eq,ls"],
    ["eq", "ls", "eq,ls"],
    ["eq", "ls", "eq,ls"],
    ["fl", "ew", "ew,fl"],
    ["fl", "ew", "ew,fl"],
    ["fl", "ew", "ew,fl"],
    ["ew", "ls", "ew,ls"],
    ["ew", "ls", "ew,ls"],
    ["ew", "ls", "ew,ls"],
    ["fl", "ls", "fl,ls"],
    ["fl", "ls", "fl,ls"],
    ["fl", "ls", "fl,ls"],
]
impacts = [
    "Total Damages, Adjusted ('000 US$')",
    "Total Affected",
    "Total Deaths",
    "Total Damages, Adjusted ('000 US$')",
    "Total Affected",
    "Total Deaths",
    "Total Damages, Adjusted ('000 US$')",
    "Total Affected",
    "Total Deaths",
    "Total Damages, Adjusted ('000 US$')",
    "Total Affected",
    "Total Deaths",
    "Total Damages, Adjusted ('000 US$')",
    "Total Affected",
    "Total Deaths",
    "Total Damages, Adjusted ('000 US$')",
    "Total Affected",
    "Total Deaths",
]

i = 0

for ax in axs.reshape(-1):
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

    # # Calculate number of obs per group & median to position labels
    # medians = df.groupby(["eventtype_detailed"])[impacts[i]].median().values
    # nobs = df["eventtype_detailed"].value_counts().values
    # nobs = [str(x) for x in nobs.tolist()]
    # nobs = ["n: " + i for i in nobs]

    # # Add it to the plot
    # pos = range(len(nobs))
    # for tick, label in zip(pos, ax.get_xticklabels()):
    #     ax.text(
    #         pos[tick],
    #         medians[tick],
    #         nobs[tick],
    #         horizontalalignment="center",
    #         size="x-small",
    #         color="w",
    #         weight="semibold",
    #     )

    i = i + 1

fig.tight_layout()


# %% Bootstrap distribution mean damages: I.e. if and only if Z = X + Y than E(Z) = E(X) + E(Y)
cols = ["sample_id", "event_type", "impact_type", "factor"]
df_bs = pd.DataFrame(
    columns=cols,
)

n = 1
N = 1000
impact_vars = ["Total Damages, Adjusted ('000 US$')", "Total Affected", "Total Deaths"]

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

# %%
