# %% Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %% Constants
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"
min_overlap_thress = [0, 0.25, 0.5, 0.75, 1]
max_time_lags = [0, 30, 91, 182, 365]

# %% Load EM-DAT
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

# Get total impact values
total_damages = df_emdat["Total Damages, Adjusted ('000 US$')"].sum()
total_affected = df_emdat["Total Affected"].sum()
total_deaths = df_emdat["Total Deaths"].sum()

# %%
df_all = (
    pd.DataFrame()
)  # dataframe to concatenate all multi-hazard events for different overlaps
no_events = (
    pd.DataFrame()
)  # Count number of total events identified for different overlaps

# %%
for min_overlap_thres in min_overlap_thress:
    for max_time_lag in max_time_lags:
        # Load MH events file
        filename = (
            "data/df_mh_events_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv"
        )
        df_mh_events = pd.read_csv(filename, sep=";")

        # Concatenate dataframes
        no_events = pd.concat(
            [
                no_events,
                pd.DataFrame(
                    [
                        {
                            "Time lag": max_time_lag,
                            "Spatial overlap": min_overlap_thres,
                            "No events": len(df_mh_events),
                            "Share mh events": sum(df_mh_events["No hazards"] > 1)
                            / len(df_mh_events),
                        }
                    ]
                ),
            ]
        )
        df_all = pd.concat([df_all, df_mh_events])


# %% Create a df with sahre of multi-hazard events and their impacts
# Do this as negative of single-hazard events as hazards can occurr in multiple multi-hazard events

# Get all single hazard events
single_filter = df_all["No hazards"] == 1
df_all_singles = df_all.loc[single_filter, :].reset_index()

# Create aggregation
df_grouped = (
    df_all[
        [
            "Time lag",
            "Spatial overlap",
            "No hazards",
            "Total damages",
            "Total affected",
            "Total deaths",
        ]
    ]
    .groupby(["Time lag", "Spatial overlap"])
    .agg("sum")
    .reset_index()
)

# Get percentages of multi-event impacts as 100% - share of single events
df_all_multi_shares = df_grouped.copy(deep=True)
df_all_multi_shares["Total damages"] = (
    100 - df_all_multi_shares["Total damages"] / total_damages * 100
)
df_all_multi_shares["Total affected"] = 100 - (
    df_all_multi_shares["Total affected"] / total_affected * 100
)
df_all_multi_shares["Total deaths"] = (
    100 - df_all_multi_shares["Total deaths"] / total_deaths * 100
)

# Add number of identified events and share of multi-hazard events
for ix, row in df_all_multi_shares.iterrows():
    no_events_filter = (no_events["Time lag"] == row["Time lag"]) & (
        no_events["Spatial overlap"] == row["Spatial overlap"]
    )
    df_all_multi_shares.loc[ix, "No events"] = no_events.loc[
        no_events_filter, "No events"
    ][0]
    df_all_multi_shares.loc[ix, "Share mh events"] = no_events.loc[
        no_events_filter, "Share mh events"
    ][0]

# Round time lag to months
df_all_multi_shares["Time lag"] = round(df_all_multi_shares["Time lag"] / 30)

# Share of mh events to %
df_all_multi_shares["Share mh events"] = df_all_multi_shares["Share mh events"] * 100

# Spatial overlap to %
df_all_multi_shares["Spatial overlap"] = df_all_multi_shares["Spatial overlap"] * 100
df_all_multi_shares["Spatial overlap"] = (
    df_all_multi_shares["Spatial overlap"].astype(int).astype(str) + "%"
)
df_all_multi_shares = df_all_multi_shares.rename(
    columns={"Spatial overlap": "Minimum spatial overlap"}
)

# %% Create plots
cp = sns.color_palette("Greys", n_colors=3)
cp2 = [cp[0], cp[1], cp[2], cp[1], cp[0]]
sns.set_style("whitegrid")
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(18, 12))

# first panel
sns.lineplot(
    data=df_all_multi_shares,
    x="Time lag",
    y="No events",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=True,
    palette=cp2,
    ax=ax1,
    markersize=12,
)
ax1.set_xlabel("Maximum time lag [months]", fontsize=20)
ax1.set_ylabel("Number of events", fontsize=20)
ax1.tick_params(labelsize=18)
ax1.set_title("(a)", fontsize=20)
ax1.set_ylim([2500, 6000])
plt.setp(ax1.get_legend().get_title(), fontsize="20")  # for legend title

# second panel
sns.lineplot(
    data=df_all_multi_shares,
    x="Time lag",
    y="Share mh events",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax2,
    markersize=12,
)
ax2.set_xlabel("Maximum time lag [months]", fontsize=20)
ax2.set_ylabel("Share of multi-hazard events [%]", fontsize=20)
ax2.tick_params(labelsize=18)
ax2.set_title("(b)", fontsize=20)
ax2.set_ylim([25, 45])


ax3.axis("off")

# third panel
sns.lineplot(
    data=df_all_multi_shares,
    x="Time lag",
    y="Total damages",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax4,
    markersize=12,
)
ax4.set_xlabel("Maximum time lag [months]", fontsize=20)
ax4.set_ylabel("Total Damages [%]", fontsize=20)
ax4.tick_params(labelsize=18)
ax4.set_title("(b)", fontsize=20)
# ax4.set_ylim([40, 100])

# fourth panel
sns.lineplot(
    data=df_all_multi_shares,
    x="Time lag",
    y="Total affected",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax5,
    markersize=12,
)
ax5.set_xlabel("Maximum time lag [months]", fontsize=20)
ax5.set_ylabel("Total affected [%]", fontsize=20)
ax5.tick_params(labelsize=18)
ax5.set_title("(c)", fontsize=20)
# ax5.set_ylim([40, 100])

# fifth panel
sns.lineplot(
    data=df_all_multi_shares,
    x="Time lag",
    y="Total deaths",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax6,
    markersize=12,
)
ax6.set_xlabel("Maximum time lag [months]", fontsize=20)
ax6.set_ylabel("Total Deaths [%]", fontsize=20)
ax6.tick_params(labelsize=18)
ax6.set_title("(d)", fontsize=20)
# ax6.set_ylim([40, 100])

# layout & legend
plt.tight_layout(pad=3)
sns.move_legend(ax1, "upper left", bbox_to_anchor=(2.6, 1.025), prop={"size": 18})

# %%
