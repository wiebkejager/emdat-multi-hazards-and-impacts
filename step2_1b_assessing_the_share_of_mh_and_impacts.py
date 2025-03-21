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
            "data/df_events_and_impacts_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv"
        )
        df_events_and_impacts = pd.read_csv(filename, sep=";")

        # Concatenate dataframes
        no_events = pd.concat(
            [
                no_events,
                pd.DataFrame(
                    [
                        {
                            "Time lag": max_time_lag,
                            "Spatial overlap": min_overlap_thres,
                            "No events": len(df_events_and_impacts),
                            "Share mhs": 1
                            - sum(df_events_and_impacts["No hazards"] == 1) / 7605,
                            "Share mh events": sum(
                                df_events_and_impacts["No hazards"] > 1
                            )
                            / len(df_events_and_impacts),
                        }
                    ]
                ),
            ]
        )
        df_all = pd.concat([df_all, df_events_and_impacts])


# %% Create a df with sahre of multi-hazard events and their impacts
# Do this as negative of single-hazard events as hazards can occurr in multiple multi-hazard events

# Get all single hazard events
single_filter = df_all["No hazards"] == 1
df_all_singles = df_all.loc[single_filter, :].reset_index()

# Create aggregation
df_grouped = (
    df_all_singles[
        [
            "Time lag",
            "Spatial overlap",
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
    df_all_multi_shares.loc[ix, "Share mhs"] = no_events.loc[
        no_events_filter, "Share mhs"
    ][0]
    df_all_multi_shares.loc[ix, "Share mh events"] = no_events.loc[
        no_events_filter, "Share mh events"
    ][0]
    df_all_multi_shares.loc[ix, "No events"] = no_events.loc[
        no_events_filter, "No events"
    ][0]

# Round time lag to months
df_all_multi_shares["Time lag"] = round(df_all_multi_shares["Time lag"] / 30)

# Share of mh events to %
df_all_multi_shares["Share mh events"] = df_all_multi_shares["Share mh events"] * 100
df_all_multi_shares["Share mhs"] = df_all_multi_shares["Share mhs"] * 100


# Spatial overlap to %
df_all_multi_shares["Spatial overlap"] = df_all_multi_shares["Spatial overlap"] * 100
df_all_multi_shares["Spatial overlap"] = (
    df_all_multi_shares["Spatial overlap"].astype(int).astype(str) + "%"
)
df_all_multi_shares = df_all_multi_shares.rename(
    columns={"Spatial overlap": "Minimum spatial overlap"}
)


# %%
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(19, 13))
gs = gridspec.GridSpec(2, 6)
ax0 = plt.subplot(
    gs[0, 0:2],
)
ax1 = plt.subplot(
    gs[0, 2:4],
)
ax2 = plt.subplot(
    gs[0, 4:6],
)
ax3 = plt.subplot(gs[1, :2])
ax4 = plt.subplot(gs[1, 2:4])
ax5 = plt.subplot(gs[1, 4:6])


cp = sns.color_palette("Greys", n_colors=3)
cp2 = [cp[0], cp[1], cp[2], cp[1], cp[0]]
sns.set_style("whitegrid")

# zeroth panel
sns.lineplot(
    data=df_all_multi_shares,
    x="Time lag",
    y="No events",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=True,
    palette=cp2,
    ax=ax0,
    markersize=12,
)
ax0.set_xlabel("Maximum time lag [months]", fontsize=20)
ax0.set_ylabel("Number of events", fontsize=20)
ax0.tick_params(labelsize=18)
ax0.set_title("(a)", fontsize=20)
ax0.set_xticks(ticks=[0, 1, 3, 6, 12])
plt.setp(ax0.get_legend().get_title(), fontsize="20")  # for legend title


# first panel
sns.lineplot(
    data=df_all_multi_shares,
    x="Time lag",
    y="Share mh events",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax1,
    markersize=12,
)
ax1.set_xlabel("Maximum time lag [months]", fontsize=20)
ax1.set_ylabel("Multi-hazard events [%]", fontsize=20)
ax1.tick_params(labelsize=18)
ax1.set_title("(b)", fontsize=20)
ax1.set_ylim([23, 47])
ax1.set_xticks(ticks=[0, 1, 3, 6, 12])

# second panel
sns.lineplot(
    data=df_all_multi_shares,
    x="Time lag",
    y="Share mhs",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax2,
    markersize=12,
)
ax2.set_xlabel("Maximum time lag [months]", fontsize=20)
ax2.set_ylabel("Hazards in multi-hazard events [%]", fontsize=20)
ax2.tick_params(labelsize=18)
ax2.set_title("(c)", fontsize=20)
ax2.set_ylim([40, 85])
ax2.set_xticks(ticks=[0, 1, 3, 6, 12])


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
    ax=ax3,
    markersize=12,
)
ax3.set_xlabel("Maximum time lag [months]", fontsize=20)
ax3.set_ylabel("Damages [%]", fontsize=20)
ax3.tick_params(labelsize=18)
ax3.set_title("(d)", fontsize=20)
ax3.set_ylim([40, 100])
ax3.set_xticks(ticks=[0, 1, 3, 6, 12])


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
    ax=ax4,
    markersize=12,
)
ax4.set_xlabel("Maximum time lag [months]", fontsize=20)
ax4.set_ylabel("People affected [%]", fontsize=20)
ax4.tick_params(labelsize=18)
ax4.set_title("(e)", fontsize=20)
ax4.set_ylim([40, 100])
ax4.set_xticks(ticks=[0, 1, 3, 6, 12])


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
    ax=ax5,
    markersize=12,
)
ax5.set_xlabel("Maximum time lag [months]", fontsize=20)
ax5.set_ylabel("Deaths [%]", fontsize=20)
ax5.tick_params(labelsize=18)
ax5.set_title("(f)", fontsize=20)
ax5.set_ylim([40, 100])
ax5.set_xticks(ticks=[0, 1, 3, 6, 12])

# layout & legend
plt.grid()
plt.tight_layout(pad=3)
sns.move_legend(
    ax0, "lower center", ncol=5, bbox_to_anchor=(1.65, -1.7), prop={"size": 18}
)

# %%
