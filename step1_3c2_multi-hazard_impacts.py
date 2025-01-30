# %% Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

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
df_events = pd.DataFrame()
no_events = pd.DataFrame()

# %%

# for min_overlap_thres in min_overlap_thress:
#     for max_time_lag in max_time_lags:

min_overlap_thres = 0.5
max_time_lag = 91

# Read file
filename = "data/df_chain_" + str(min_overlap_thres) + "_" + str(max_time_lag) + ".csv"          
df_chain = pd.read_csv(filename, sep=";")

# Sort records column to make looping faster
df_chain.sort_values(by = "Events")

# Convert string of events to list of events 
df_chain["Events"] = df_chain["Events"].apply(json.loads)

#%%
# Create multi-hazard events set
df_mh_events = df_chain.copy(deep = True)

# Drop duplicates
for ix, irow in df_chain.iterrows():
    is_subset = False
    for jx, jrow in df_chain.iterrows():                      
        # Check if chain is included in another chain 
        if ix != jx:
            is_subset = set(irow["Events"]).issubset(jrow["Events"]) 
            # If chain is included in another chain drop from multi-hazard events df
            if is_subset == True:
                df_mh_events.drop(ix, inplace = True)
                break

#%%
# Add impact metrics
for ix, row in df_mh_events.iterrows():
    deaths = 0
    affected = 0
    damage = 0
    for record in row["Events"]:
        deaths = (deaths + df_emdat.loc[record, "Total Deaths"]).sum()
        affected = (affected + df_emdat.loc[record, "Total Affected"]).sum()
        damage = (damage + df_emdat.loc[record, "Total Damages, Adjusted ('000 US$')"]).sum()  
    df_mh_events.loc[ix,"Total deaths"] = deaths
    df_mh_events.loc[ix,"Total affected"] = affected
    df_mh_events.loc[ix,"Total damages"] = damage

# Add information on time lag and overlap for later analysis
df_mh_events.loc[:,"Time lag"] = max_time_lag
df_mh_events.loc[:,"Spatial overlap"] = min_overlap_thres

df_mh_events.drop(df_mh_events.columns[0], axis = 1, inplace= True)

#%%
# Save
df_mh_events.to_csv(
    "data/df_mh_events"
    + str(min_overlap_thres)
    + "_"
    + str(max_time_lag)
    + ".csv",
    sep=";",
    index=False,
)

#%%



        # # Add damages to each event
        # for ix, row in df.iterrows():
        #     records = json.loads(row["Events"])
        #     deaths = 0
        #     affected = 0
        #     damage = 0
        #     for record in records:
        #         deaths = (deaths + df_emdat.loc[record, "Total Deaths"]).sum()
        #         affected = (affected + df_emdat.loc[record, "Total Affected"]).sum()
        #         damage = (damage + df_emdat.loc[record, "Total Damages, Adjusted ('000 US$')"]).sum()                      
 
        #     df.loc[ix,"Total deaths"] = deaths
        #     df.loc[ix,"Total affected"] = affected
        #     df.loc[ix,"Total damages"] = damage
        #     df.loc[ix,"Time lag"] = max_time_lag
        #     df.loc[ix,"Spatial overlap"] = min_overlap_thres

        #     df.loc[ix,"Event type"] = "Single"
        #     if df.loc[ix,"No hazards"] > 1:
        #         df.loc[ix,"Event type"] = "Multi"    
                
        # no_events = pd.concat([no_events,pd.DataFrame([{"Time lag": max_time_lag,"Spatial overlap": min_overlap_thres,"Number events": len(df)}])])
        # df_events = pd.concat([df_events,df])


# %%
df_plot = (
    df_events[
        [
            "Time lag",
            "Spatial overlap",
            "Event type",
            "No hazards",
            "Total damages",
            "Total affected",
            "Total deaths",
        ]
    ]
    .groupby(["Time lag", "Spatial overlap", "Event type"])
    .agg("sum")
    .reset_index()
)


# %%
df_plot["Total damages"] = 100 - df_plot["Total damages"] / total_damages * 100
df_plot["Total affected"] = 100 - (
    df_plot["Total affected"] / total_affected * 100
)
df_plot["Total deaths"] = 100 - df_plot["Total deaths"] / total_deaths * 100

df_plot["Time lag"] = round(df_plot["Time lag"] / 30)

# %%
df_plot = df_plot.rename(columns={"No hazards": "Number of single hazards"})
df_plot["Proportion of hazards"] = 100 - (
    df_plot["Number of single hazards"] / NO_HAZARDS * 100
)

df_plot["Spatial overlap"] = df_plot["Spatial overlap"] * 100
df_plot["Spatial overlap"] = df_plot["Spatial overlap"].astype(int).astype(str) + "%"
df_plot = df_plot.rename(columns={"Spatial overlap": "Minimum spatial overlap"})

#%%
mutli_filter = df_plot["Event type"] == "Single"

# %% color palette
cp = sns.color_palette("Greys", n_colors=3)
cp2 = [cp[0], cp[1], cp[2], cp[1], cp[0]]

# %%
sns.set_style("whitegrid")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

sns.lineplot(
    data=df_plot[mutli_filter],
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

sns.lineplot(
    data=df_plot[mutli_filter],
    x="Time lag",
    y="Total damages",
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
    data=df_plot[mutli_filter],
    x="Time lag",
    y="Total affected",
    hue="Minimum spatial overlap",
    style="Minimum spatial overlap",
    markers=True,
    legend=False,
    palette=cp2,
    ax=ax3,
    markersize=12,
)

ax3.set_xlabel("Maximum time lag [months]", fontsize=20)
ax3.set_ylabel("Total affected [%]", fontsize=20)
ax3.tick_params(labelsize=18)
ax3.set_title("(c)", fontsize=20)
ax3.set_ylim([40, 100])

# ax.set_title("Single Hazards in EM-DAT 2000 - 2018", fontsize = 20)
# plt.setp(ax3.get_legend().get_texts(), fontsize="20")  # for legend text
# plt.setp(ax3.get_legend().get_title(), fontsize="20")  # for legend title
plt.tight_layout()

sns.lineplot(
    data=df_plot[mutli_filter],
    x="Time lag",
    y="Total deaths",
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
