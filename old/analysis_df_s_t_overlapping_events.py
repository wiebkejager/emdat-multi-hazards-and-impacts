# %% Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np

# %%
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %% EM-DAT
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df_emdat.loc[:, "Hazards"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: list(x.dropna()), axis=1
)
df_emdat.loc[:, "No Hazards"] = df_emdat.loc[:, "Hazards"].apply(len)


# %% s-t overlapping events
df_s_t_overlapping_events_50percent = pd.read_csv(
    "data/df_s_t_overlapping_events_50percent.csv", sep=";", index_col=0
)
df_s_t_overlapping_events_50percent["Min spatial overlap"] = 0.5


df_s_t_overlapping_events_100percent = pd.read_csv(
    "data/df_s_t_overlapping_events_100percent.csv", sep=";", index_col=0
)
df_s_t_overlapping_events_100percent["Min spatial overlap"] = 1


df = pd.concat(
    [df_s_t_overlapping_events_50percent, df_s_t_overlapping_events_100percent],
    ignore_index=True,
)

# %% Count number of events
df["Events"] = df["Events"].apply(json.loads)
df["No events"] = df["Events"].apply(len)


# %% Add hazards and count number of hazards
for ix, row in df.iterrows():
    events = row.loc["Events"]
    hazards = []
    damages = []
    affected = []
    deaths = []
    for event in events:
        hazards = hazards + list(
            df_emdat.loc[event, ["Hazard1", "Hazard2", "Hazard3"]].dropna().values
        )
        damages = damages + [df_emdat.loc[event, "Total Damages, Adjusted ('000 US$')"]]
        affected = affected + [df_emdat.loc[event, "Total Affected"]]
        deaths = deaths + [df_emdat.loc[event, "Total Deaths"]]

    df.loc[ix, "Hazards"] = json.dumps(hazards)
    df.loc[ix, "Damages"] = np.nansum(damages)
    df.loc[ix, "Affected"] = np.nansum(affected)
    df.loc[ix, "Deaths"] = np.nansum(deaths)


df["Hazards"] = df["Hazards"].apply(json.loads)
df["No hazards"] = df["Hazards"].apply(len)
df["Type"] = "Single hazard"
df.loc[df["No hazards"] > 1, "Type"] = "Multi hazard"

# %%
TIME_LAGS = df["Timelag"].unique()

df_plot_50 = pd.DataFrame(
    columns=[
        "Event sets",
        "Number of events without overlap",
        "Number of events with overlap",
        "Number of hazards without overlap",
        "Number of hazards with overlap",
    ]
)
df_plot_100 = pd.DataFrame(
    columns=[
        "Event sets",
        "Number of events without overlap",
        "Number of events with overlap",
        "Number of hazards without overlap",
        "Number of hazards with overlap",
    ]
)

for TIME_LAG in TIME_LAGS:
    df_temp = df.loc[(df["Timelag"] == TIME_LAG) & (df["Min spatial overlap"] == 0.5)]
    df_plot_50.loc[TIME_LAG, "Number of events without overlap"] = sum(
        df_temp["No events"] == 1
    )
    df_plot_50.loc[TIME_LAG, "Number of events with overlap"] = (
        len(df_emdat) - df_plot_50.loc[TIME_LAG, "Number of events without overlap"]
    )
    df_plot_50.loc[TIME_LAG, "Event sets"] = len(df_temp)
    df_plot_50.loc[TIME_LAG, "Number of hazards without overlap"] = sum(
        df_temp["No hazards"] == 1
    )
    df_plot_50.loc[TIME_LAG, "Number of hazards with overlap"] = (
        df_temp["No hazards"].sum()
        - df_plot_50.loc[TIME_LAG, "Number of hazards without overlap"]
    )

for TIME_LAG in TIME_LAGS:
    df_temp = df.loc[(df["Timelag"] == TIME_LAG) & (df["Min spatial overlap"] == 1)]
    df_plot_100.loc[TIME_LAG, "Number of events without overlap"] = sum(
        df_temp["No events"] == 1
    )
    df_plot_100.loc[TIME_LAG, "Number of events with overlap"] = (
        len(df_emdat) - df_plot_100.loc[TIME_LAG, "Number of events without overlap"]
    )
    df_plot_100.loc[TIME_LAG, "Event sets"] = len(df_temp)
    df_plot_100.loc[TIME_LAG, "Number of hazards without overlap"] = sum(
        df_temp["No hazards"] == 1
    )
    df_plot_100.loc[TIME_LAG, "Number of hazards with overlap"] = (
        df_temp["No hazards"].sum()
        - df_plot_100.loc[TIME_LAG, "Number of hazards without overlap"]
    )

# %%
df_plot_50["Min spatial overlap"] = "50%"
df_plot_100["Min spatial overlap"] = "50%"

# %%
# df_plot = pd.concat([df_plot_50.reset_index(), df_plot_100.reset_index()]).rename(
#     columns={"index": "Timelag"}
# )


# %%
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3))
sns.set_style("whitegrid")
sns.lineplot(
    data=df_plot_50.drop(
        columns=[
            "Event sets",
            "Number of hazards with overlap",
            "Number of events with overlap",
        ]
    ).loc[TIME_LAGS[0:5]],
    markers=True,
    ax=ax1,
    legend=False,
)
ax1.set(
    ylabel="Number",
    xlabel="Time lag in days",
    title="Min. spatial overlap = 50%",
    ylim=(500, 6000),
)

sns.set_style("whitegrid")
sns.lineplot(
    data=df_plot_100.drop(
        columns=[
            "Event sets",
            "Number of hazards with overlap",
            "Number of events with overlap",
        ]
    ).loc[TIME_LAGS[0:5]],
    markers=True,
    ax=ax2,
)
ax2.set(
    ylabel="Number",
    xlabel="Time lag in days",
    title="Min. spatial overlap = 100%",
    ylim=(500, 6000),
)

sns.move_legend(ax2, "upper left", bbox_to_anchor=(1, 1))


# %% Damage plots
timelag_filter = df["Timelag"].isin([0, 30, 91, 182, 365])
df_total_impacts = (
    df[timelag_filter]
    .groupby(["Timelag", "Min spatial overlap", "Type"])
    .sum()[["Damages", "Affected", "Deaths"]]
).reset_index()

# %%
df_total_impacts_plot = df_total_impacts
df_total_impacts_plot["Criterion"] = (
    (df_total_impacts_plot["Min spatial overlap"] * 100).apply(str)
    + "%, "
    + df_total_impacts_plot["Timelag"].apply(str)
    + " days"
)
df_total_impacts_plot = df_total_impacts_plot.drop(
    ["Min spatial overlap", "Timelag"], axis=1
)

# %%
fig, (ax1, ax2, ax3) = plt.subplots(
    1,
    3,
    figsize=(12, 3),
)
sns.histplot(
    df_total_impacts_plot,
    y="Criterion",
    weights="Damages",
    hue="Type",
    multiple="stack",
    palette=["#24b1d1", "#ae24d1"],
    # Add white borders to the bars.
    edgecolor="white",
    shrink=0.8,
    ax=ax1,
    legend=False,
)
ax1.tick_params(axis="x", rotation=90)
ax1.set_xlabel("Total Damages")

sns.histplot(
    df_total_impacts_plot,
    y="Criterion",
    weights="Affected",
    hue="Type",
    multiple="stack",
    palette=["#24b1d1", "#ae24d1"],
    # Add white borders to the bars.
    edgecolor="white",
    shrink=0.8,
    ax=ax2,
    legend=False,
)
ax2.tick_params(axis="x", rotation=90)
ax2.set_xlabel("Total people affected")

sns.histplot(
    df_total_impacts_plot,
    y="Criterion",
    weights="Deaths",
    hue="Type",
    multiple="stack",
    palette=["#24b1d1", "#ae24d1"],
    # Add white borders to the bars.
    edgecolor="white",
    shrink=0.8,
    ax=ax3,
    legend=True,
)
ax3.tick_params(axis="x", rotation=90)
ax3.set_xlabel("Total deaths")


sns.move_legend(
    ax3,
    "upper left",
    bbox_to_anchor=(1, 0.5),
    # ncol=3,
    title=None,
    frameon=False,
)

fig.tight_layout()
# sns.barplot(df_total_impacts_plot, x="Criterion", y="Damages", hue="Type", ax=ax1)
# sns.barplot(df_total_impacts_plot, x="Criterion", y="Affected", hue="Type", ax=ax2)
# sns.barplot(df_total_impacts_plot, x="Criterion", y="Deaths", hue="Type", ax=ax3)

# sns.catplot(
#     df_total_impacts_plot, kind="bar", x="Type", y="Damages", col="Criterion", ax=ax1
# )
# sns.catplot(
#     df_total_impacts_plot, kind="bar", x="Type", y="Affected", col="Criterion", ax=ax2
# )
# sns.catplot(
#     df_total_impacts_plot, kind="bar", x="Type", y="Deaths", col="Criterion", ax=ax3
# )

# %%
