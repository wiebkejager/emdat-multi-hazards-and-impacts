# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %% Constants
PROCESSED_EMDAT_PATH = "C:/Users/wja209/DATA/PROCESSED/emdat_2000_2015.csv"

# %%
df = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

# %% Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: "multi-hazard" if sum(x.isna()) <= 1 else "single-hazard", axis=1
)
# Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype_detailed"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)

# Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype_detailed_unsrt"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(list(x.dropna())), axis=1
)

# %%
event_counts = df.loc[:, "eventtype_detailed"].value_counts()
event_counts.to_csv("event_counts.csv", sep=";")

# %%
event_counts_unsrt = df.loc[:, "eventtype_detailed_unsrt"].value_counts()
hazards = sorted(event_counts_unsrt[event_counts_unsrt >= 10].index)
hazards.remove("vo")
hazards.remove("ts,ts")

# %%
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


# %%
fig, (ax1, ax2) = plt.subplots(1, 2, width_ratios=[1, 9])
hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazards)
sns.boxplot(
    x="eventtype",
    y="Total Deaths",
    data=df[hazard_filter],
    ax=ax1,
    showfliers=False,
).set(xlabel=None)
ax1.grid()
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_ylabel("Count of events")
ax1.set_title("(a)")

sns.boxplot(
    x="eventtype_detailed_unsrt",
    y="Total Deaths",
    data=df[hazard_filter],
    ax=ax2,
    showfliers=False,
    order=hazards,
).set(xlabel=None)
ax2.grid()
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
ax2.set_ylabel("Count of events")
ax2.set_title("(b)")
fig.tight_layout()

# %%
hazard_groups = [
    ["fl", "ew", "ew,fl"],
    # ["fl", "ew", "ls", "ew,fl", "ew,ls", "ew,fl,ls"],
    ["ew", "cw", "cw,ew"],
    # ["dr", "hw", "dr,hw"],
    # ["eq", "ls", "eq,ls"],
]

fig, (ax1, ax2, ax3) = plt.subplots(
    1,
    3,
    figsize=(10, 5),
    width_ratios=[2, 3, 3],
)

hazard_filter = df.loc[:, "eventtype_detailed"].isin(
    [item for sublist in hazard_groups for item in sublist]
)
sns.countplot(x="eventtype", data=df[hazard_filter], ax=ax1).set(xlabel=None)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_title("(a)")
ax1.grid()

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[0])
sns.countplot(
    x="eventtype_detailed",
    data=df[hazard_filter],
    ax=ax2,
    order=hazard_groups[0],
).set(xlabel=None)
ax2.grid()
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
ax2.set_title("(b)")

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[1])
sns.countplot(
    x="eventtype_detailed",
    data=df[hazard_filter],
    ax=ax3,
    order=hazard_groups[1],
).set(xlabel=None)
ax3.grid()
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
ax3.set_title("(c)")

# hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[2])
# sns.countplot(
#     x="eventtype_detailed",
#     data=df[hazard_filter],
#     ax=ax4,
#     order=hazard_groups[2],
# ).set(xlabel=None)
# ax4.grid()
# ax4.set_xticklabels(ax4.get_xticklabels(), rotation=90)
# ax4.set_title("(d)")

# hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[3])
# sns.countplot(
#     x="eventtype_detailed",
#     data=df[hazard_filter],
#     ax=ax5,
#     order=hazard_groups[3],
# ).set(xlabel=None)
# ax5.grid()
# ax5.set_xticklabels(ax5.get_xticklabels(), rotation=90)
# ax5.set_title("(e)")

fig.tight_layout()

# %%
hazard_groups = [
    ["fl", "ew", "ew,fl"],
    # ["fl", "ew", "ls", "ew,fl", "ew,ls", "ew,fl,ls"],
    ["ew", "cw", "cw,ew"],
    # ["dr", "hw", "dr,hw"],
    # ["eq", "ls", "eq,ls"],
]

fig, (ax1, ax2, ax3) = plt.subplots(
    1,
    3,
    figsize=(10, 5),
    width_ratios=[2, 3, 3],
)

hazard_filter = df.loc[:, "eventtype_detailed"].isin(
    [item for sublist in hazard_groups for item in sublist]
)
sns.boxplot(
    x="eventtype", y="Total Deaths", data=df[hazard_filter], ax=ax1, showfliers=False
).set(xlabel=None)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_title("(a)")
ax1.grid()

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[0])
sns.boxplot(
    x="eventtype_detailed",
    y="Total Deaths",
    data=df[hazard_filter],
    ax=ax2,
    order=hazard_groups[0],
    showfliers=False,
).set(xlabel=None)
ax2.grid()
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
ax2.set_title("(b)")

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[1])
sns.boxplot(
    x="eventtype_detailed",
    y="Total Deaths",
    data=df[hazard_filter],
    ax=ax3,
    order=hazard_groups[1],
    showfliers=False,
).set(xlabel=None)
ax3.grid()
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
ax3.set_title("(c)")

# hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[2])
# sns.boxplot(
#     x="eventtype_detailed",
#     y="Total Deaths",
#     data=df[hazard_filter],
#     ax=ax4,
#     order=hazard_groups[2],
#     showfliers=False,
# ).set(xlabel=None)
# ax4.grid()
# ax4.set_xticklabels(ax4.get_xticklabels(), rotation=90)
# ax4.set_title("(d)")

# hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[3])
# sns.boxplot(
#     x="eventtype_detailed",
#     y="Total Deaths",
#     data=df[hazard_filter],
#     ax=ax5,
#     order=hazard_groups[3],
#     showfliers=False,
# ).set(xlabel=None)
# ax5.grid()
# ax5.set_xticklabels(ax5.get_xticklabels(), rotation=90)
# ax5.set_title("(e)")

fig.tight_layout()


# %%
hazard_groups = [
    ["fl", "ew", "ew,fl"],
    # ["fl", "ew", "ls", "ew,fl", "ew,ls", "ew,fl,ls"],
    ["ew", "cw", "cw,ew"],
    # ["dr", "hw", "dr,hw"],
    # ["eq", "ls", "eq,ls"],
]

fig, (ax1, ax2, ax3) = plt.subplots(
    1,
    3,
    figsize=(10, 5),
    width_ratios=[2, 3, 3],
)

hazard_filter = df.loc[:, "eventtype_detailed"].isin(
    [item for sublist in hazard_groups for item in sublist]
)
sns.boxplot(
    x="eventtype", y="Total Affected", data=df[hazard_filter], ax=ax1, showfliers=False
).set(xlabel=None)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_title("(a)")
ax1.grid()

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[0])
sns.boxplot(
    x="eventtype_detailed",
    y="Total Affected",
    data=df[hazard_filter],
    ax=ax2,
    order=hazard_groups[0],
    showfliers=False,
).set(xlabel=None)
ax2.grid()
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
ax2.set_title("(b)")

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[1])
sns.boxplot(
    x="eventtype_detailed",
    y="Total Affected",
    data=df[hazard_filter],
    ax=ax3,
    order=hazard_groups[1],
    showfliers=False,
).set(xlabel=None)
ax3.grid()
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
ax3.set_title("(c)")

# hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[2])
# sns.boxplot(
#     x="eventtype_detailed",
#     y="Total Affected",
#     data=df[hazard_filter],
#     ax=ax4,
#     order=hazard_groups[2],
#     showfliers=False,
# ).set(xlabel=None)
# ax4.grid()
# ax4.set_xticklabels(ax4.get_xticklabels(), rotation=90)
# ax4.set_title("(d)")

# hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[3])
# sns.boxplot(
#     x="eventtype_detailed",
#     y="Total Deaths",
#     data=df[hazard_filter],
#     ax=ax5,
#     order=hazard_groups[3],
#     showfliers=False,
# ).set(xlabel=None)
# ax5.grid()
# ax5.set_xticklabels(ax5.get_xticklabels(), rotation=90)
# ax5.set_title("(e)")

fig.tight_layout()


# %%
hazard_groups = [
    ["fl", "ew", "ew,fl"],
    # ["fl", "ew", "ls", "ew,fl", "ew,ls", "ew,fl,ls"],
    ["ew", "cw", "cw,ew"],
    # ["dr", "hw", "dr,hw"],
    # ["eq", "ls", "eq,ls"],
]

fig, (ax1, ax2, ax3) = plt.subplots(
    1,
    3,
    figsize=(10, 5),
    width_ratios=[2, 3, 3],
)

hazard_filter = df.loc[:, "eventtype_detailed"].isin(
    [item for sublist in hazard_groups for item in sublist]
)
sns.boxplot(
    x="eventtype",
    y="Total Damages, Adjusted ('000 US$')",
    data=df[hazard_filter],
    ax=ax1,
    showfliers=False,
).set(xlabel=None)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_title("(a)")
ax1.grid()

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[0])
sns.boxplot(
    x="eventtype_detailed",
    y="Total Damages, Adjusted ('000 US$')",
    data=df[hazard_filter],
    ax=ax2,
    order=hazard_groups[0],
    showfliers=False,
).set(xlabel=None)
ax2.grid()
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
ax2.set_title("(b)")

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[1])
sns.boxplot(
    x="eventtype_detailed",
    y="Total Damages, Adjusted ('000 US$')",
    data=df[hazard_filter],
    ax=ax3,
    order=hazard_groups[1],
    showfliers=False,
).set(xlabel=None)
ax3.grid()
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
ax3.set_title("(c)")

# hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[2])
# sns.boxplot(
#     x="eventtype_detailed",
#     y="Total Damages, Adjusted ('000 US$')",
#     data=df[hazard_filter],
#     ax=ax4,
#     order=hazard_groups[2],
#     showfliers=False,
# ).set(xlabel=None)
# ax4.grid()
# ax4.set_xticklabels(ax4.get_xticklabels(), rotation=90)
# ax4.set_title("(d)")

# hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_groups[3])
# sns.boxplot(
#     x="eventtype_detailed",
#     y="Total Damages, Adjusted ('000 US$')",
#     data=df[hazard_filter],
#     ax=ax5,
#     order=hazard_groups[3],
#     showfliers=False,
# ).set(xlabel=None)
# ax5.grid()
# ax5.set_xticklabels(ax5.get_xticklabels(), rotation=90)
# ax5.set_title("(e)")

fig.tight_layout()

# %% Correlations event types
indices = [
    "fl",
    "ew",
    "cw",
    "dr",
    "hw",
    "ls",
    "eq",
    "ew,fl",
    "cw,ew",
    "dr,hw",
    "ew,ls",
    "eq,ls",
    "ew,fl,ls",
]
cols = [
    "Event Count",
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
            data.loc[index, col] = np.sum(~df.loc[event_filter, col].isna())
            # np.round(
            #     (
            #         np.sum(~df.loc[event_filter, col].isna())
            #         / data.loc[index, "Event Count"]
            #     ),
            #     #     2,
            #     ),
            # ]

print(data)


data.to_csv("available_data_count.csv", sep=";")


# %%
hazard_group = ["fl", "ew", "ew,fl"]

fig, (ax3, ax4, ax2) = plt.subplots(
    1,
    3,
    figsize=(10, 5),
    width_ratios=[3, 3, 3],
)


hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_group)
sns.boxplot(
    x="eventtype_detailed",
    y="Total Damages, Adjusted ('000 US$')",
    data=df[hazard_filter],
    ax=ax2,
    order=hazard_group,
    showfliers=False,
).set(xlabel=None)
ax2.grid()
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
ax2.set_title("(b)")

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_group)
sns.boxplot(
    x="eventtype_detailed",
    y="Total Deaths",
    data=df[hazard_filter],
    ax=ax3,
    order=hazard_group,
    showfliers=False,
).set(xlabel=None)
ax3.grid()
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
ax3.set_title("(c)")

hazard_filter = df.loc[:, "eventtype_detailed"].isin(hazard_group)
sns.boxplot(
    x="eventtype_detailed",
    y="Total Affected",
    data=df[hazard_filter],
    ax=ax4,
    order=hazard_group,
    showfliers=False,
).set(xlabel=None)
ax4.grid()
ax4.set_xticklabels(ax4.get_xticklabels(), rotation=90)
ax4.set_title("(c)")


fig.tight_layout()
# %%
