# %% Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

# %%
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %% EM-DAT
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
df_emdat.loc[:, "Hazards"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: list(x.dropna()), axis=1
)
df_emdat.loc[:, "No Hazards"] = df_emdat.loc[:, "Hazards"].apply(len)


# %% s-t overlapping events
df = pd.read_csv("data/df_s_t_overlapping_events.csv", sep=";", index_col=0)


# %% Count number of events
df["Events"] = df["Events"].apply(json.loads)
df["No events"] = df["Events"].apply(len)


# %% Add hazards and count number of hazards
for ix, row in df.iterrows():
    events = row.loc["Events"]
    hazards = []
    for event in events:
        hazards = hazards + list(
            df_emdat.loc[event, ["Hazard1", "Hazard2", "Hazard3"]].dropna().values
        )

    df.loc[ix, "Hazards"] = json.dumps(hazards)

df["Hazards"] = df["Hazards"].apply(json.loads)
df["No hazards"] = df["Hazards"].apply(len)


# %%
TIME_LAGS = df["Timelag"].unique()

df_plot = pd.DataFrame(
    columns=[
        "non_overlapping_events",
        "overlapping_events",
        "idependent_sets_events",
        "average_events",
        "max_events",
    ]
)

for TIME_LAG in TIME_LAGS[0:4]:
    df_temp = df.loc[df["Timelag"] == TIME_LAG]
    df_plot.loc[TIME_LAG, "non_overlapping_events"] = sum(df_temp["No events"] == 1)
    df_plot.loc[TIME_LAG, "overlapping_events"] = (
        len(df_emdat) - df_plot.loc[TIME_LAG, "non_overlapping_events"]
    )
    df_plot.loc[TIME_LAG, "idependent_sets_events"] = len(df_temp)
    df_plot.loc[TIME_LAG, "non_overlapping_hazards"] = sum(df_temp["No hazards"] == 1)
    df_plot.loc[TIME_LAG, "overlapping_hazards"] = (
        len(df_emdat) - df_plot.loc[TIME_LAG, "non_overlapping_hazards"]
    )


# %%

fig, (ax1) = plt.subplots(1)
sns.set_style("whitegrid")
sns.lineplot(
    data=df_plot,
    markers=True,
    ax=ax1,
)
ax1.set(ylabel="Number", xlabel="Time lag in days")
sns.move_legend(ax1, "upper left", bbox_to_anchor=(1, 1))
