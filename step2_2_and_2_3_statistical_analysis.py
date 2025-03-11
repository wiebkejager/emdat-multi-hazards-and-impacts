###
# This file analysis the preprocessed EMDAT data

# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from my_functions import get_bs_sample_df, get_impact_mean

# %% Constants
min_overlap_thres = 0.5
max_time_lag = 91

# %% Read file with single hazards and hazard pairs
df_all = pd.read_csv(
    "data/df_single_and_pair_impacts_"
    + str(min_overlap_thres)
    + "_"
    + str(max_time_lag)
    + ".csv",
    sep=";",
)

# %% Add impacts to single hazards and hazard pairs
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


# %% Function for bootstrap distribution mean damages: I.e. if and only if Z = X + Y than E(Z) = E(X) + E(Y)
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
    N = 10000

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

        n = n + 1

    return df_bs


# %% Run function for bootstrap distribution mean damages
df_bs = bootstrap(df)


# %% Plot results
sns.set_style("whitegrid")
fig, axs = plt.subplots(3, 4, figsize=(20, 20), facecolor="0.95")

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

logscale = [
    False,
    False,
    False,
    False,
    True,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
]

titles = [
    "Extreme winds and floods",
    "Floods and floods",
    "Floods and landslides",
    "Earthquakes and landslides",
]

i = -1

for ax in axs.reshape(-1):
    i = i + 1
    hazard_group = hazard_groups[i]
    hazard_filter = df_bs.loc[:, "event_type"].isin(hazard_group)

    impact = ""
    if impacts[i] == "Total Damages $1 billion":
        impact = "Damages [$1 billion]"
    if impacts[i] == "Total Deaths":
        impact = "Deaths"
    if impacts[i] == "Total Affected":
        impact = "People affected"

    sns.pointplot(
        ax=ax,
        x="wholesum",
        y=impacts[i],
        data=df_bs[hazard_filter],
        errorbar=("pi", 0),
        linestyle="none",
        legend=False,
        palette=sns.color_palette("Greys", n_colors=1),
        log_scale=logscale[i],
    ).set(xlabel="", ylabel="")

    hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_group)
    sns.boxplot(
        x="eventtype_detailed",
        y=impacts[i],
        data=df[hazard_filter],
        ax=ax,
        order=hazard_group,
        showfliers=False,
        boxprops={"fill": None},
    ).set(xlabel="", ylabel="")

    hazard_filter = df_bs.loc[:, "event_type"].isin(hazard_group)

    sns.pointplot(
        ax=ax,
        x="wholesum",
        y=impacts[i],
        data=df_bs[hazard_filter],
        linestyle="none",
        errorbar=("pi", 90),
        markers="|",
        legend=False,
        palette=sns.color_palette("Greys", n_colors=1),
        capsize=0.1,
    ).set(xlabel="", ylabel="")

    ax.tick_params(labelsize=20, rotation=45)
    ax.set_xticklabels(
        ax.get_xticklabels(),
        fontsize=20,
    )

    if i in [0, 4, 8]:
        ax.set_ylabel(impact, fontsize=25, labelpad=25, weight="bold")

    if i in [0, 1, 2, 3]:
        ax.set_title(titles[i], fontsize=25, pad=25, weight="bold")

fig.tight_layout(pad=2)
