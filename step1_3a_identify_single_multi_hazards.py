# %% Imports
import pandas as pd
import matplotlib.pyplot as plt
from itertools import chain
import seaborn as sns

FIRST_YEAR = 2000
LAST_YEAR = 2018
PROCESSED_IMPACT_PATH_CSV = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"
NO_HAZARDS = 7605

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
unique_events_sorted = df_emdat.sort_values(by="Start Date").index.values


# %%
total_damages = df_emdat["Total Damages, Adjusted ('000 US$')"].sum()
total_affected = df_emdat["Total Affected"].sum()
total_deaths = df_emdat["Total Deaths"].sum()


# %%
min_overlap_thress = [0, 0.25, 0.5, 0.75, 1]
max_time_lags = [0, 30, 91, 182, 365]


# %%
df_single_records = pd.DataFrame()


# %%
# min_overlap_thres = 1
# max_time_lag = 0
for min_overlap_thres in min_overlap_thress:
    for max_time_lag in max_time_lags:

        filename = (
            "data/event_pairs_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv"
        )
        df = pd.read_csv(filename, sep=";")
        event_pairs = list(
            df.loc[:, ["Event1", "Event2"]].itertuples(index=False, name=None)
        )
        events_with_overlap = list(chain.from_iterable(event_pairs))

        for unique_event in unique_events_sorted:
            if unique_event not in events_with_overlap:
                new_row = pd.DataFrame(
                    [
                        {
                            "Event": unique_event,
                            "Time lag": max_time_lag,
                            "Spatial overlap": min_overlap_thres,
                            "No hazards": len(
                                df_emdat.loc[
                                    unique_event, ["Hazard1", "Hazard2", "Hazard3"]
                                ]
                                .dropna()
                                .values
                            ),
                            "Total Damages": df_emdat.loc[
                                unique_event, "Total Damages, Adjusted ('000 US$')"
                            ],
                            "Total People Affected": df_emdat.loc[
                                unique_event, "Total Affected"
                            ],
                            "Total Deaths": df_emdat.loc[unique_event, "Total Deaths"],
                        }
                    ]
                )
                df_single_records = pd.concat([df_single_records, new_row])


# %%
hazard_filter = df_single_records["No hazards"] == 1
df_single_hazards = df_single_records[hazard_filter]

# %%
df_plot = (
    df_single_hazards[
        [
            "Time lag",
            "Spatial overlap",
            "No hazards",
            "Total Damages",
            "Total People Affected",
            "Total Deaths",
        ]
    ]
    .groupby(["Time lag", "Spatial overlap"])
    .agg("sum")
    .reset_index()
)


# %%
df_plot["Total Damages"] = 100 - df_plot["Total Damages"] / total_damages * 100
df_plot["Total People Affected"] = 100 - (
    df_plot["Total People Affected"] / total_affected * 100
)
df_plot["Total Deaths"] = 100 - df_plot["Total Deaths"] / total_deaths * 100

df_plot["Time lag"] = round(df_plot["Time lag"] / 30)

# %%
df_plot = df_plot.rename(columns={"No hazards": "Number of single hazards"})
df_plot["Proportion of hazards"] = 100 - (
    df_plot["Number of single hazards"] / NO_HAZARDS * 100
)
df_plot["Spatial overlap"] = df_plot["Spatial overlap"] * 100
df_plot["Spatial overlap"] = df_plot["Spatial overlap"].astype(int).astype(str) + "%"

# %%
overlap_filter = (df_plot["Spatial overlap"] >= "25%") & (
    df_plot["Spatial overlap"] <= "75%"
)
df_plot = df_plot.rename(columns={"Spatial overlap": "Minimum spatial overlap"})


# %% color palette
cp = sns.color_palette("Greys", n_colors=3)
cp2 = [cp[0], cp[1], cp[2], cp[1], cp[0]]

# %%
sns.set_style("whitegrid")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

sns.lineplot(
    data=df_plot,
    x="Time lag",
    y="Proportion of hazards",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=True,
    palette=cp2,
    ax=ax1,
    markersize=12,
)

ax1.set_xlabel("Maximum time lag [months]", fontsize=20)
ax1.set_ylabel("Hazards [%]", fontsize=20)
ax1.tick_params(labelsize=18)
ax1.set_title("(a)", fontsize=20)
ax1.set_ylim([40, 100])
plt.setp(ax1.get_legend().get_title(), fontsize="20")  # for legend title


# ax.set_title("Single Hazards in EM-DAT 2000 - 2018", fontsize = 20)
# plt.setp(ax1.get_legend().get_texts(), fontsize="20")  # for legend text
# plt.setp(ax1.get_legend().get_title(), fontsize="20")  # for legend title


sns.lineplot(
    data=df_plot,
    x="Time lag",
    y="Total Damages",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax2,
    markersize=12,
)

ax2.set_xlabel("Maximum time lag [months]", fontsize=20)
ax2.set_ylabel("Total Damages [%]", fontsize=20)
ax2.tick_params(labelsize=18)
ax2.set_title("(b)", fontsize=20)
ax2.set_ylim([40, 100])


# ax.set_title("Single Hazards in EM-DAT 2000 - 2018", fontsize = 20)
plt.tight_layout()

sns.lineplot(
    data=df_plot,
    x="Time lag",
    y="Total People Affected",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax3,
    markersize=12,
)

ax3.set_xlabel("Maximum time lag [months]", fontsize=20)
ax3.set_ylabel("Total People Affected [%]", fontsize=20)
ax3.tick_params(labelsize=18)
ax3.set_title("(c)", fontsize=20)
ax3.set_ylim([40, 100])

# ax.set_title("Single Hazards in EM-DAT 2000 - 2018", fontsize = 20)
# plt.setp(ax3.get_legend().get_texts(), fontsize="20")  # for legend text
# plt.setp(ax3.get_legend().get_title(), fontsize="20")  # for legend title
plt.tight_layout()

sns.lineplot(
    data=df_plot,
    x="Time lag",
    y="Total Deaths",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax4,
    markersize=12,
)

ax4.set_xlabel("Maximum time lag [months]", fontsize=20)
ax4.set_ylabel("Total Deaths [%]", fontsize=20)
ax4.tick_params(labelsize=18)
ax4.set_title("(d)", fontsize=20)
ax4.set_ylim([40, 100])

# # plt.setp(ax4.get_legend().get_texts(), fontsize="20")  # for legend text
# plt.setp(ax4.get_legend().get_title(), fontsize="20")  # for legend title
plt.tight_layout(pad=3)

sns.move_legend(ax1, "upper left", bbox_to_anchor=(2.3, 1.025), prop={"size": 18})


# %%
