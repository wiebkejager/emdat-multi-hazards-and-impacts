###
# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from my_functions import get_bs_sample_df, get_impact_mean


# %%
df_all = pd.read_csv("data/df_single_and_pair_impacts.csv", sep=";")
time_lag_filter = df_all["Timelag"] == 6935
df_all = df_all[~time_lag_filter]

# %%
impact_dam = "Total Damages 1"
impact_aff = "Total Affected 1"
impact_dea = "Total Deaths 1"

single_event_counts_dam = (
    df_all.dropna(subset=impact_dam)
    .loc[:, ["Hazard 1", "Timelag"]]
    .value_counts()
    .rename(index="Total Damages")
)
single_event_counts_aff = (
    df_all.dropna(subset=impact_aff)
    .loc[:, ["Hazard 1", "Timelag"]]
    .value_counts()
    .rename(index="Total Affected")
)
single_event_counts_dea = (
    df_all.dropna(subset=impact_dea)
    .loc[:, ["Hazard 1", "Timelag"]]
    .value_counts()
    .rename(index="Total Deaths")
)
single_event_counts = pd.concat(
    [single_event_counts_dam, single_event_counts_aff, single_event_counts_dea], axis=1
).sort_index()

single_event_counts.to_csv("data/single_events_data_availability.csv")


# %%
impact_dam = "Total Damages 12"
impact_aff = "Total Affected 12"
impact_dea = "Total Deaths 12"

double_event_counts_dam = (
    df_all.dropna(subset=impact_dam)
    .loc[:, ["Hazard 1", "Hazard 2", "Timelag"]]
    .value_counts()
    .rename(index="Total Damages")
)
double_event_counts_aff = (
    df_all.dropna(subset=impact_aff)
    .loc[:, ["Hazard 1", "Hazard 2", "Timelag"]]
    .value_counts()
    .rename(index="Total Affected")
)
double_event_counts_dea = (
    df_all.dropna(subset=impact_dea)
    .loc[:, ["Hazard 1", "Hazard 2", "Timelag"]]
    .value_counts()
    .rename(index="Total Deaths")
)

double_event_counts = pd.concat(
    [double_event_counts_dam, double_event_counts_aff, double_event_counts_dea], axis=1
).sort_index()

double_event_counts.to_csv("data/double_events_data_availability.csv")

# %%

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
        "Total Damages 12": "Total Damages",
    }
)
df = pd.concat([df1, df2]).reset_index()


# Add column indicating event sequence
df.loc[:, "eventtype_detailed"] = df[["Hazard 1", "Hazard 2"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)


# %% plot singles
single_hazards = df1["Hazard 1"].unique()
fig, axs = plt.subplots(
    9,
    3,
    figsize=(12, 24),
)

impacts = ["Total Damages", "Total Affected", "Total Deaths"]

i = -1
j = -1
for ax in axs.reshape(-1):
    j = j + 1
    if j > 2:
        j = 0
        i = i + 1

    # if i > 8:
    #     i = 0
    hazard_filter = df1.loc[:, "Hazard 1"] == single_hazards[i]
    sns.boxplot(
        x="Timelag",
        y=impacts[j],
        data=df1[hazard_filter],
        ax=ax,
        showfliers=False,
        showmeans=True,
        meanprops={
            # "marker": "s",
            "markerfacecolor": "red",
            "markeredgecolor": "red",
        },
    ).set(xlabel="Time lag")
    # ax.semilogy(base=2)
    # ax.grid()
    ax.set_xticklabels(ax.get_xticklabels())
    ax.set_title(single_hazards[i])
    # medians = df[hazard_filter].groupby(["Timelag"])[impacts[j]].quantile(q=0.5).values
    # nobs = df[hazard_filter]["Timelag"].value_counts().values
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
    #         size="medium",
    #         color="r",
    #         weight="bold",
    #     )

fig.tight_layout()


# %% plot singles
single_hazards = ["fl", "fl", "fl"]  # df1["Hazard 1"].unique()
fig, axs = plt.subplots(
    1,
    3,
    figsize=(12, 24),
)

impacts = ["Total Damages", "Total Affected", "Total Deaths"]

i = -1
j = -1
for ax in axs.reshape(-1):
    j = j + 1
    if j > 2:
        j = 0
        i = i + 1

    # if i > 8:
    #     i = 0
    hazard_filter = df1.loc[:, "Hazard 1"] == single_hazards[i]
    sns.boxplot(
        x="Timelag",
        y=impacts[j],
        data=df1[hazard_filter],
        ax=ax,
        # showfliers=False,
        showmeans=True,
        meanprops={
            # "marker": "s",
            "markerfacecolor": "red",
            "markeredgecolor": "red",
        },
    ).set(xlabel="Time lag")
    # ax.semilogy(base=2)
    # ax.grid()
    ax.set_xticklabels(ax.get_xticklabels())
    ax.set_title(single_hazards[i])
    # medians = df[hazard_filter].groupby(["Timelag"])[impacts[j]].quantile(q=0.5).values
    # nobs = df[hazard_filter]["Timelag"].value_counts().values
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
    #         size="medium",
    #         color="r",
    #         weight="bold",
    #     )

fig.tight_layout()


# %%
timelag = 182
df = df[df["Timelag"] == timelag]

# %%
fig, axs = plt.subplots(
    4,
    3,
    figsize=(12, 16),
    # width_ratios=[3, 3, 3],
)
hazard_groups = [
    ["ew", "fl", "ew,fl"],
    ["ew", "fl", "ew,fl"],
    ["ew", "fl", "ew,fl"],
    ["fl", "ls", "fl,ls"],
    ["fl", "ls", "fl,ls"],
    ["fl", "ls", "fl,ls"],
    ["fl", "fl", "fl,fl"],
    ["fl", "fl", "fl,fl"],
    ["fl", "fl", "fl,fl"],
    ["eq", "ls", "eq,ls"],
    ["eq", "ls", "eq,ls"],
    ["eq", "ls", "eq,ls"],
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
        showmeans=True,
        meanprops={
            # "marker": "s",
            "markerfacecolor": "yellow",
            "markeredgecolor": "yellow",
        },
    ).set(xlabel="Hazard Type")
    # ax.semilogy(base=2)
    ax.grid()
    ax.set_xticklabels(ax.get_xticklabels())

    medians = (
        df[hazard_filter]
        .groupby(["eventtype_detailed"])[impacts[i]]
        .quantile(q=0.5)
        .values
    )
    nobs = df[hazard_filter]["eventtype_detailed"].value_counts().values
    nobs = [str(x) for x in nobs.tolist()]
    nobs = ["n: " + i for i in nobs]

    # Add it to the plot
    pos = range(len(nobs))
    for tick, label in zip(pos, ax.get_xticklabels()):
        ax.text(
            pos[tick],
            medians[tick],
            nobs[tick],
            horizontalalignment="center",
            size="medium",
            color="r",
            weight="bold",
        )

fig.suptitle("Timelag: " + str(timelag), fontsize=16)
fig.tight_layout()

# %%
df_means = (
    df[["Total Damages", "Total Affected", "Total Deaths", "eventtype_detailed"]]
    .groupby(["eventtype_detailed"])
    .mean()
)

df_means.loc[
    ["ew", "fl", "ls", "eq", "fl,ls", "ew,fl", "fl,fl", "eq,ls"]
].round().to_csv("data/sum_and_whole_damages.csv", sep=";")

# %%
hazard_pairs = ["fl,ls", "ew,fl", "fl,fl", "eq,ls"]

# %%

# %% Bootstrap distribution mean damages: I.e. if and only if Z = X + Y than E(Z) = E(X) + E(Y)
cols = [
    "sample_id",
    "event_type",
    "Total Damages",
    "Total Affected",
    "Total Deaths",
    "wholesum",
]
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

        whole_damages = get_impact_mean(df_bs_haz12, "Total Damages")
        haz1_damages = get_impact_mean(df_bs_haz1, "Total Damages")
        haz2_damages = get_impact_mean(df_bs_haz2, "Total Damages")
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
                    "Whole",
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
                    "Sum",
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
                    "Haz1",
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
                    "Haz2",
                ]
            ],
            columns=cols,
        )

        df_bs = pd.concat([df_bs, new_row3], ignore_index=True)
        df_bs = pd.concat([df_bs, new_row4], ignore_index=True)
        df_bs = pd.concat([df_bs, new_row2], ignore_index=True)
        df_bs = pd.concat([df_bs, new_row1], ignore_index=True)

    n = n + 1


# %%
fig, axs = plt.subplots(4, 3, figsize=(12, 12))

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
]

i = -1
for ax in axs.reshape(-1):
    i = i + 1
    hazard_group = hazard_groups[i]
    hazard_filter = df_bs.loc[:, "event_type"].isin(hazard_group)

    # sns.boxplot(
    #     ax=ax,
    #     x="event_type",
    #     y=impacts[i],
    #     hue="wholesum",
    #     data=df_bs[hazard_filter],
    #     showfliers=False,
    # )
    sns.pointplot(
        ax=ax,
        x="Timelag",
        y=impacts[i],
        hue="wholesum",
        data=df_bs[hazard_filter],
        dodge=0.2,
        join=False,
        errorbar=("pi", 95),
        markers="|",
        legend=False,
    )

    ax.set_title(hazard_group)

    sns.pointplot(
        ax=ax,
        x="event_type",
        y=impacts[i],
        hue="wholesum",
        data=df_bs[hazard_filter],
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

    ax.yaxis.grid(True)  # Hide the horizontal

# fig.suptitle("Timelag: " + str(timelag), fontsize=16)
fig.tight_layout()

# %%
