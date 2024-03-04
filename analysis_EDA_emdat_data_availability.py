###
# This file analysis the preprocessed EMDAT data


# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import missingno as msno

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
event_counts = df.loc[:, ["eventtype_detailed", "Continent"]].value_counts()

# hazards = sorted(event_counts[event_counts >= 20].index)


# %%
foo = event_counts.reset_index().pivot_table(
    "count", ["eventtype_detailed"], "Continent"
)
foo.plot.bar(stacked=True)


# %% Show count of events
fig, (ax1, ax2) = plt.subplots(1, 2, width_ratios=[1, 9])
hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazards)
sns.countplot(x="eventtype", data=df[hazard_filter], ax=ax1).set(xlabel=None)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_ylabel("Count of events")
ax1.set_title("(a)")
for p in ax1.patches:
    ax1.annotate(
        "{:.0f}".format(p.get_height()), (p.get_x() - 0.1, p.get_height() + 0.01)
    )

sns.countplot(
    x="eventtype_detailed_unsrt", data=df[hazard_filter], ax=ax2, order=hazards
).set(xlabel=None)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
ax2.set_ylabel("Count of events")
ax2.set_title("(b)")
for p in ax2.patches:
    ax2.annotate(
        "{:.0f}".format(p.get_height()), (p.get_x() - 0.1, p.get_height() + 0.01)
    )
fig.tight_layout()

# %% Get missing data per event type

# indices = [
#     "fl",
#     "ew",
#     "cw",
#     "dr",
#     "hw",
#     "ls",
#     "eq",
#     "ew,fl",
#     "cw,ew",
#     "dr,hw",
#     "ew,ls",
#     "eq,ls",
#     "ew,fl,ls",
# ]

indices = hazards

cols = [
    "Event Count",
    "Start Date",
    "End Date",
    "Dis Mag Value",
    "Total Deaths",
    "Total Affected",
    "Total Damages, Adjusted ('000 US$')",
]
data = pd.DataFrame(
    index=indices,
    columns=cols,
)

for index in indices:
    event_filter = df["eventtype_detailed"] == index
    for col in cols:
        if col == "Event Count":
            data.loc[index, col] = len(df[event_filter])
        else:
            data.loc[index, col] = (
                np.sum(~df.loc[event_filter, col].isna())
                / data.loc[index, "Event Count"]
            )

print(data)

# %%
data_indicator = data.copy(deep=True)

data_indicator["Total Deaths"] = (data_indicator["Total Deaths"] >= 0.5) & (
    data_indicator["Total Deaths"] * data_indicator["Event Count"] >= 20
)
data_indicator["Total Affected"] = (data_indicator["Total Affected"] >= 0.5) & (
    data_indicator["Total Affected"] * data_indicator["Event Count"] >= 20
)
data_indicator["Total Damages, Adjusted ('000 US$')"] = (
    data_indicator["Total Damages, Adjusted ('000 US$')"] >= 0.5
) & (
    data_indicator["Total Damages, Adjusted ('000 US$')"]
    * data_indicator["Event Count"]
    >= 20
)
data_indicator = data_indicator.drop(
    ["Event Count", "Start Date", "End Date", "Dis Mag Value"], axis=1
)

# %%
data.to_csv("available_data.csv", sep=";")
data_indicator.reset_index().rename({"index": "event_type"}, axis=1).to_csv(
    "data_indicator.csv", sep=";", index=False
)

# %%
# impact_var = "Total Damages, Adjusted ('000 US$')"
impact_var = "Total Affected"
# impact_var = "Total Deaths"

# %%
indices = list(df["Continent"].unique())
data1 = pd.DataFrame(
    index=indices,
    columns=["Missing", "Available"],
)
data2 = pd.DataFrame(
    index=indices,
    columns=["Missing", "Available"],
)

for index in indices:
    filter = df["Continent"] == index
    data1.loc[index, "Missing"] = (
        df.loc[filter, impact_var].isna().sum()  # / filter.sum()
    )
    data1.loc[index, "Available"] = (
        ~df.loc[filter, impact_var].isna()
    ).sum()  # / filter.sum()
    data2.loc[index, "Missing"] = df.loc[filter, impact_var].isna().sum() / filter.sum()
    data2.loc[index, "Available"] = (
        ~df.loc[filter, impact_var].isna()
    ).sum() / filter.sum()

ax1 = data1.plot.bar(rot=45, stacked=True)
ax1.set_title(impact_var)

ax2 = data2.plot.bar(rot=45, stacked=True)
ax2.set_title(impact_var)

data1["Percentage"] = data1["Available"] / (data1["Missing"] + data1["Available"])

# %%
indices = hazards
data1 = pd.DataFrame(
    index=indices,
    columns=["Missing", "Available"],
)
data2 = pd.DataFrame(
    index=indices,
    columns=["Missing", "Available"],
)

for index in indices:
    filter = df["eventtype_detailed"] == index
    data1.loc[index, "Missing"] = (
        df.loc[filter, impact_var].isna().sum()  # / filter.sum()
    )
    data1.loc[index, "Available"] = (
        ~df.loc[filter, impact_var].isna()
    ).sum()  # / filter.sum()
    data2.loc[index, "Missing"] = df.loc[filter, impact_var].isna().sum() / filter.sum()
    data2.loc[index, "Available"] = (
        ~df.loc[filter, impact_var].isna()
    ).sum() / filter.sum()

ax1 = data1.plot.bar(rot=45, stacked=True)
ax1.set_title(impact_var)

ax2 = data2.plot.bar(rot=45, stacked=True)
ax2.set_title(impact_var)


# %%
indices = df.index.str[0:4].unique()
data1 = pd.DataFrame(
    index=indices,
    columns=["Missing", "Available"],
)
data2 = pd.DataFrame(
    index=indices,
    columns=["Missing", "Available"],
)


for index in indices:
    filter = df.index.str[0:4] == index
    data1.loc[index, "Missing"] = (
        df.loc[filter, impact_var].isna().sum()  # / filter.sum()
    )
    data1.loc[index, "Available"] = (
        ~df.loc[filter, impact_var].isna()
    ).sum()  # / filter.sum()
    data2.loc[index, "Missing"] = df.loc[filter, impact_var].isna().sum() / filter.sum()
    data2.loc[index, "Available"] = (
        ~df.loc[filter, impact_var].isna()
    ).sum() / filter.sum()

ax1 = data1.plot.bar(rot=45, stacked=True)
ax1.set_title(impact_var)

ax2 = data2.plot.bar(rot=45, stacked=True)
ax2.set_title(impact_var)

# for c in ax.containers:
#     ax.bar_label(c, label_type="center")

# %%
df["Country"].value_counts()

# %%
