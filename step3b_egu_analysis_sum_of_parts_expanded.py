###
# This file analysis the preprocessed EMDAT data

# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from my_functions import get_bs_sample_df, get_impact_mean

# %% Constants
# %% Constants
min_overlap_thres = 0.5
max_time_lag = 91
# %%
df_all = pd.read_csv(
    "data/df_single_and_pair_impacts_"
    + str(min_overlap_thres)
    + "_"
    + str(max_time_lag)
    + ".csv",
    sep=";",
)

# %%
df1 = df_all.loc[
    :, ["Hazard 1", "Total Deaths 1", "Total Affected 1", "Total Damages 1", "Timelag"]
].dropna(how="all", subset=["Total Deaths 1", "Total Affected 1", "Total Damages 1"])
df1["Event"] = "Single"
df1["Hazard 2"] = np.nan
df1 = df1.rename(
    columns={
        "Total Deaths 1": "Total Deaths",
        "Total Affected 1": "Total Affected",
        "Total Damages 1": "Total Damages $1 billion",
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
        "Timelag",
    ],
].dropna(
    how="all",
    subset=["Total Deaths 12", "Total Affected 12", "Total Damages 12"],
)
df2["Event"] = "Double"
df2 = df2.rename(
    columns={
        "Total Deaths 12": "Total Deaths",
        "Total Affected 12": "Total Affected",
        "Total Damages 12": "Total Damages $1 billion",
    }
)
df = pd.concat([df1, df2]).reset_index()


# Add column indicating event sequence
df.loc[:, "eventtype_detailed"] = df[["Hazard 1", "Hazard 2"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)


df["Total Damages $1 billion"] = df["Total Damages $1 billion"] / (10**6)

# %%


# %%
# df_means = (
#     df[["Total Damages", "Total Affected", "Total Deaths", "eventtype_detailed"]]
#     .groupby(["eventtype_detailed"])
#     .mean()
# )

# df_means.loc[
#     ["ew", "fl", "ls", "eq", "fl,ls", "ew,fl", "fl,fl", "eq,ls"]
# ].round().to_csv("data/sum_and_whole_damages.csv", sep=";")


# %%
# event_counts = df.loc[:, ["eventtype_detailed"]].value_counts()
# event_counts.reset_index().plot.bar(rot=45, stacked=True)
# hazards = sorted(event_counts[event_counts >= 25].index)


# # %% Compare mean damages: I.e. if and only if Z = X + Y than E(Z) = E(X) + E(Y)
# iterables = [
#     ["Total Damages", "Total Affected", "Total Deaths"],
#     ["whole", "sum", "whole/sum"],
# ]
# index = pd.MultiIndex.from_product(iterables, names=["first", "second"])
# df_res = pd.DataFrame(index=index, columns=hazard_pairs)

# for hazard_pair in hazard_pairs:
#     ## Damages
#     # pairs
#     df_res.loc[index[0], hazard_pair] = df.loc[
#         df.loc[:, "eventtype_detailed"] == hazard_pair, index[0][0]
#     ].mean()
#     # sum
#     [haz1, haz2] = hazard_pair.split(",")
#     df_res.loc[index[1], hazard_pair] = (
#         df.loc[df.loc[:, "eventtype_detailed"] == haz1, index[0][0]].mean()
#         + df.loc[df.loc[:, "eventtype_detailed"] == haz2, index[0][0]].mean()
#     )
#     # sum/pairs
#     df_res.loc[index[2], hazard_pair] = (
#         df_res.loc[index[0], hazard_pair] / df_res.loc[index[1], hazard_pair]
#     )
#     ## Affected
#     # pairs
#     df_res.loc[index[3], hazard_pair] = df.loc[
#         df.loc[:, "eventtype_detailed"] == hazard_pair, index[3][0]
#     ].mean()
#     # sum
#     [haz1, haz2] = hazard_pair.split(",")
#     df_res.loc[index[4], hazard_pair] = (
#         df.loc[df.loc[:, "eventtype_detailed"] == haz1, index[3][0]].mean()
#         + df.loc[df.loc[:, "eventtype_detailed"] == haz2, index[3][0]].mean()
#     )
#     # sum/pairs
#     df_res.loc[index[5], hazard_pair] = (
#         df_res.loc[index[3], hazard_pair] / df_res.loc[index[4], hazard_pair]
#     )

#     ## Deaths
#     # pairs
#     df_res.loc[index[6], hazard_pair] = df.loc[
#         df.loc[:, "eventtype_detailed"] == hazard_pair, index[6][0]
#     ].mean()
#     # sum
#     [haz1, haz2] = hazard_pair.split(",")
#     df_res.loc[index[7], hazard_pair] = (
#         df.loc[df.loc[:, "eventtype_detailed"] == haz1, index[6][0]].mean()
#         + df.loc[df.loc[:, "eventtype_detailed"] == haz2, index[6][0]].mean()
#     )
#     # sum/pairs
#     df_res.loc[index[8], hazard_pair] = (
#         df_res.loc[index[6], hazard_pair] / df_res.loc[index[7], hazard_pair]
#     )

# df_res = df_res.astype("float64").round(1)
# df_res.to_csv("data/sum_and_whole_damages.csv", sep=";")


# %% Bootstrap distribution mean damages: I.e. if and only if Z = X + Y than E(Z) = E(X) + E(Y)
def bootstrap(df) -> pd.DataFrame:
    # hazard_pairs = ["ew,fl"]
    hazard_pairs = ["fl,ls", "ew,fl", "eq,ls", "fl,fl"]

    cols = [
        "sample_id",
        "event_type",
        "Total Damages $1 billion",
        "Total Affected",
        "Total Deaths",
        "wholesum",
    ]
    df_bs = pd.DataFrame(
        columns=cols,
    )

    n = 1
    N = 1000

    for hazard_pair in hazard_pairs:
        [haz1, haz2] = hazard_pair.split(",")
        for n in range(N):
            df_bs_haz1 = get_bs_sample_df(df, haz1)
            df_bs_haz2 = get_bs_sample_df(df, haz2)
            df_bs_haz12 = get_bs_sample_df(df, hazard_pair)

            whole_damages = get_impact_mean(df_bs_haz12, "Total Damages $1 billion")
            haz1_damages = get_impact_mean(df_bs_haz1, "Total Damages $1 billion")
            haz2_damages = get_impact_mean(df_bs_haz2, "Total Damages $1 billion")
            sum_damages = haz1_damages + haz2_damages

            whole_affected = get_impact_mean(df_bs_haz12, "Total Affected")
            haz1_affected = get_impact_mean(df_bs_haz1, "Total Affected")
            haz2_affected = get_impact_mean(df_bs_haz2, "Total Affected")
            sum_affected = haz1_affected + haz2_affected

            whole_deaths = get_impact_mean(df_bs_haz12, "Total Deaths")
            haz1_deaths = get_impact_mean(df_bs_haz1, "Total Deaths")
            haz2_deaths = get_impact_mean(df_bs_haz2, "Total Deaths")
            sum_deaths = haz1_deaths + haz2_deaths

            new_row1 = pd.DataFrame(
                [
                    [
                        n,
                        hazard_pair,
                        whole_damages,
                        whole_affected,
                        whole_deaths,
                        hazard_pair,
                    ]
                ],
                columns=cols,
            )
            new_row2 = pd.DataFrame(
                [
                    [
                        n,
                        hazard_pair,
                        sum_damages,
                        sum_affected,
                        sum_deaths,
                        haz1 + "+" + haz2,
                    ]
                ],
                columns=cols,
            )

            new_row5 = pd.DataFrame(
                [
                    [
                        n,
                        hazard_pair,
                        whole_damages - sum_damages,
                        whole_affected - sum_affected,
                        whole_deaths - sum_deaths,
                        hazard_pair + "-" + haz1 + "-" + haz2,
                    ]
                ],
                columns=cols,
            )
            new_row3 = pd.DataFrame(
                [
                    [
                        n,
                        hazard_pair,
                        haz1_damages,
                        haz1_affected,
                        haz1_deaths,
                        haz1,
                    ]
                ],
                columns=cols,
            )
            new_row4 = pd.DataFrame(
                [
                    [
                        n,
                        hazard_pair,
                        haz2_damages,
                        haz2_affected,
                        haz2_deaths,
                        haz2,
                    ]
                ],
                columns=cols,
            )

            df_bs = pd.concat([df_bs, new_row3], ignore_index=True)
            df_bs = pd.concat([df_bs, new_row4], ignore_index=True)
            df_bs = pd.concat([df_bs, new_row1], ignore_index=True)
            df_bs = pd.concat([df_bs, new_row2], ignore_index=True)

            # df_bs = pd.concat([df_bs, new_row5], ignore_index=True)

        n = n + 1

    return df_bs


# %%
df_bs = bootstrap(df)


# %%
sns.set_style("whitegrid")
fig, axs = plt.subplots(
    3,
    4,
    figsize=(12, 20),
)
hazard_groups = [
    ["ew", "fl", "ew,fl"],
    ["fl", "fl", "fl,fl"],
    ["fl", "ls", "fl,ls"],
    ["eq", "ls", "eq,ls"],
    ["ew", "fl", "ew,fl"],
    ["fl", "fl", "fl,fl"],
    ["fl", "ls", "fl,ls"],
    ["eq", "ls", "eq,ls"],
    ["ew", "fl", "ew,fl"],
    ["fl", "fl", "fl,fl"],
    ["fl", "ls", "fl,ls"],
    ["eq", "ls", "eq,ls"],
]
impacts = [
    "Total Damages $1 billion",
    "Total Damages $1 billion",
    "Total Damages $1 billion",
    "Total Damages $1 billion",
    "Total Deaths",
    "Total Deaths",
    "Total Deaths",
    "Total Deaths",
    "Total Affected",
    "Total Affected",
    "Total Affected",
    "Total Affected",
]

i = -1

for ax in axs.reshape(-1):
    i = i + 1
    hazard_group = hazard_groups[i]


    hazard_filter = df_bs.loc[:, "event_type"].isin(hazard_group)


    sns.pointplot(
        ax=ax,
        x="wholesum",
        y=impacts[i],
        data=df_bs[hazard_filter],
        errorbar=("pi", 0),
        linestyle="none",
        legend=False,
        palette=sns.color_palette("Greys", n_colors=1),
    ).set(xlabel="")


    hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_group)
    sns.boxplot(
        x="eventtype_detailed",
        y=impacts[i],
        data=df[hazard_filter],
        ax=ax,
        order=hazard_group,
        showfliers=False,
        # showmeans=True,
        # meanprops={
        #     "markerfacecolor": sns.color_palette("Greys", n_colors=1)[0],
        #     "markeredgecolor": sns.color_palette("Greys", n_colors=1)[0],
        #     "marker": "o",
        #     "markersize": "7",
        #     # "alpha": 0,
        # },
        # color="white",
        boxprops={'fill': None}
    ).set(xlabel="")

    hazard_filter = df_bs.loc[:, "event_type"].isin(hazard_group)

    sns.pointplot(
        ax=ax,
        x="wholesum",
        y=impacts[i],
        data=df_bs[hazard_filter],
        linestyle="none",
        errorbar=("pi", 95),
        markers="|",
        legend=False,
        palette=sns.color_palette("Greys", n_colors=1),
        capsize=0.1,
    ).set(xlabel="")

    ax.set_ylabel(impacts[i], fontsize=15)
    ax.tick_params(labelsize=10, rotation = 45)
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=15, )

fig.tight_layout(pad=3)

# %%
# sns.set_style("whitegrid")

# fig, axs = plt.subplots(3, 4, figsize=(12, 9))

# impacts = [
#     "Total Damages $1 billion",
#     "Total Damages $1 billion",
#     "Total Damages $1 billion",
#     "Total Damages $1 billion",
#     "Total Deaths",
#     "Total Deaths",
#     "Total Deaths",
#     "Total Deaths",
#     "Total Affected",
#     "Total Affected",
#     "Total Affected",
#     "Total Affected",
# ]

# i = -1
# for ax in axs.reshape(-1):
#     i = i + 1
#     hazard_group = hazard_groups[i]
#     hazard_filter = df_bs.loc[:, "event_type"].isin(hazard_group)

#     sns.pointplot(
#         ax=ax,
#         x="wholesum",
#         y=impacts[i],
#         data=df_bs[hazard_filter],
#         dodge=0.4,
#         linestyle="none",
#         errorbar=("pi", 95),
#         markers="|",
#         legend=False,
#         palette=sns.color_palette("Greys", n_colors=1),
#         capsize=0.1,
#       ).set(xlabel="")

#     sns.pointplot(
#         ax=ax,
#         x="wholesum",
#         y=impacts[i],
#         # hue="wholesum",
#         data=df_bs[hazard_filter],
#         dodge=0.4,
#         errorbar=("pi", 0),
#         linestyle="none",
#         legend=False,
#         palette=sns.color_palette("Greys", n_colors=1),
#     ).set(xlabel="")

#     sns.boxplot(
#         ax=ax,
#         x="event_type",
#         y=impacts[i],
#         hue="wholesum",
#         data=df_bs[hazard_filter],
#         showfliers=False,
#     )

#     ax.set_ylabel(impacts[i], fontsize=15)
#     ax.tick_params(labelsize=10)
#     ax.set_xticklabels(ax.get_xticklabels(), fontsize=15)
#     # ax.yaxis.grid(True)  # Hide the horizontal gridlines

#     # if i==1:
#     #     ax.semilogy(base=10)
#     # ax.set_ylim(0, 3.25)


# fig.tight_layout(pad=3)

# # %%

# %%
