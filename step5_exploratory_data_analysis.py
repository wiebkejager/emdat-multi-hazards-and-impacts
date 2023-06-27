# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import statsmodels.api as sm

# %% Constants
PROCESSED_IMPACT_PATH2_CSV = "C:/Users/wja209/DATA/PROCESSED/impact_hazard_exposure_vulnerability_2000_2015_continuous.csv"
PROCESSED_EMDAT_PATH = "C:/Users/wja209/DATA/PROCESSED/emdat_2000_2015.csv"
PROCESSED_IMPACT_PATH_SINGLE_CSV = "C:/Users/wja209/DATA/PROCESSED/df_single.csv"
PROCESSED_IMPACT_PATH_MULTI_CSV = "C:/Users/wja209/DATA/PROCESSED/df_multi.csv"

# %% Read data set
df_all = pd.read_csv(PROCESSED_IMPACT_PATH2_CSV).set_index("Dis No")
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

# %% Temporary fix:
df_all.loc[:, "Total Deaths"] = df_emdat.loc[:, "Total Deaths"]

# %%
df_all = df_all.dropna(
    subset=[
        "Total Deaths",
        "Population Count",
        "GDP per Capita PPP",
    ]
)
# %% Add column indicating single-hazard or multi-hazard
df_all.loc[:, "eventtype"] = df_all[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: "multi-hazard" if sum(x.isna()) <= 1 else "single-hazard", axis=1
)
# Add column indicating single-hazard or multi-hazard
df_all.loc[:, "eventtype_detailed"] = df_all[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)

df_emdat.loc[:, "eventtype"] = df_emdat[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: "multi-hazard" if sum(x.isna()) <= 1 else "single-hazard", axis=1
)
# Add column indicating single-hazard or multi-hazard
df_emdat.loc[:, "eventtype_detailed"] = df_emdat[
    ["Hazard1", "Hazard2", "Hazard3"]
].apply(lambda x: ",".join(sorted(list(x.dropna()))), axis=1)


# %%
hazards = ["fl", "ew", "ls", "eq"]

hazard_filter = (
    (df_all["Hazard1"].isin(hazards))
    & ((df_all["Hazard2"].isin(hazards)) | df_all["Hazard2"].isna())
    & ((df_all["Hazard3"].isin(hazards)) | df_all["Hazard3"].isna())
    & (df_all["Hazard1"] != df_all["Hazard2"])
)

df = df_all[hazard_filter]

# %% Reorder
order = list(["fl", "eq", "ew", "fl,ls", "ls", "ew,fl", "eq,ls", "ew,fl,ls", "ew,ls"])


# %%
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(5, 5))
sns.countplot(x="eventtype", data=df, ax=ax1).set(xlabel=None)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax1.set_ylabel("Count of events")
sns.boxplot(x="eventtype", y="Total Affected", data=df, showfliers=False, ax=ax2).set(
    xlabel=None
)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
sns.boxplot(x="eventtype", y="Total Deaths", data=df, showfliers=False, ax=ax3).set(
    xlabel=None
)
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=90)
fig.tight_layout()


# %%
fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(10, 10))
sns.countplot(x="eventtype_detailed", data=df, ax=ax0, order=order).set(xlabel=None)
ax0.set_xticklabels(ax0.get_xticklabels(), rotation=90)
sns.boxplot(
    x="eventtype_detailed",
    y="Total Affected",
    data=df,
    ax=ax1,
    showfliers=False,
    order=order,
).set(xlabel=None)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
sns.boxplot(
    x="eventtype_detailed",
    y="Total Deaths",
    data=df,
    ax=ax2,
    showfliers=False,
    order=order,
).set(xlabel=None)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
fig.tight_layout()

# %% Quick fix: Replace 0 with na
df.loc[:, ["Intensity_fl", "Intensity_eq", "Intensity_ew", "Intensity_ls"]] = df.loc[
    :, ["Intensity_fl", "Intensity_eq", "Intensity_ew", "Intensity_ls"]
]  # .replace(0, np.nan)


# %%
multi_filter = df["eventtype"] == "multi-hazard"

# %%
fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2, figsize=(10, 10))
sns.kdeplot(x="Intensity_fl", data=df, hue="eventtype", ax=ax0)
ax0.axvline(x=df.loc[multi_filter, "Intensity_fl"].mean(), color="orange")
ax0.axvline(x=df.loc[~multi_filter, "Intensity_fl"].mean(), color="#49759c")
sns.kdeplot(x="Intensity_eq", data=df, hue="eventtype", ax=ax1)
ax1.axvline(x=df.loc[multi_filter, "Intensity_eq"].mean(), color="orange")
ax1.axvline(x=df.loc[~multi_filter, "Intensity_eq"].mean(), color="#49759c")
sns.kdeplot(x="Intensity_ew", data=df, hue="eventtype", ax=ax2)
ax2.axvline(x=df.loc[multi_filter, "Intensity_ew"].mean(), color="orange")
ax2.axvline(x=df.loc[~multi_filter, "Intensity_ew"].mean(), color="#49759c")
sns.kdeplot(x="Intensity_ls", data=df, hue="eventtype", ax=ax3)
ax3.axvline(x=df.loc[multi_filter, "Intensity_ls"].mean(), color="orange")
ax3.axvline(x=df.loc[~multi_filter, "Intensity_ls"].mean(), color="#49759c")


# %%
df["otaTl Deaths"] = df["Total Deaths"] + np.random.normal(0, 1, size=len(df))
df["Intensity_fl"] = df["Intensity_fl"] + np.random.normal(0, 1, size=len(df))
df["Intensity_eq"] = df["Intensity_eq"] + np.random.normal(0, 1, size=len(df))
df["Intensity_ew"] = df["Intensity_ew"] + np.random.normal(0, 1, size=len(df))
df["Intensity_ls"] = df["Intensity_ls"] + np.random.normal(0, 1, size=len(df))


vars = [
    "Total Deaths",
    "Population Count",
    "GDP per Capita PPP",
    "Intensity_fl",
    "Intensity_eq",
    "Intensity_ew",
    "Intensity_ls",
]

death_filter = df["otaTl Deaths"] < 2000

sns.pairplot(
    df.loc[
        death_filter,
        vars,
    ].replace(0, np.nan),
    diag_kind="kde",
)

# %%
df_ranks = df.copy()
df_ranks.loc[:, vars] = (
    df_ranks.loc[:, vars].rank() / df_ranks.loc[:, vars].rank().max()
)
sns.pairplot(df_ranks.loc[:, vars], diag_kind="hist")


# %%
detailed_types = df["eventtype_detailed"].unique()
columns = [
    "Population Count",
    "GDP per Capita PPP",
    "Intensity_fl",
    "Intensity_eq",
    "Intensity_ew",
    "Intensity_ls",
    "Sample size",
]
correlations_deaths = pd.DataFrame(
    index=detailed_types,
    columns=columns,
)

correlations_deaths_all = pd.DataFrame(
    columns=columns,
)

correlations_affected = pd.DataFrame(
    index=detailed_types,
    columns=columns,
)

# %%
for detailed_type in detailed_types:
    event_filter = df["eventtype_detailed"] == detailed_type
    df_ranks = df.copy()
    df_ranks.loc[event_filter, vars] = (
        df_ranks.loc[event_filter, vars].rank()
        / df_ranks.loc[event_filter, vars].rank().max()
    )
    sns.pairplot(df_ranks.loc[event_filter, vars], diag_kind="hist")

# %%
for detailed_type in detailed_types:
    event_filter = df["eventtype_detailed"] == detailed_type
    correlations_deaths.loc[detailed_type, "Sample size"] = sum(event_filter)
    for column in columns[0:6]:
        try:
            corr = scipy.stats.spearmanr(
                df.loc[event_filter, column],
                df.loc[event_filter, "Total Deaths"],
                nan_policy="omit",
            )
        except:
            corr = list([np.nan, np.nan])

        # if corr[1] <= 0.05:
        correlations_deaths.loc[detailed_type, column] = np.round(corr[0], 2)

# %%
for column in columns[0:6]:
    correlations_deaths_all.loc[0, "Sample size"] = sum(event_filter)

    corr = scipy.stats.spearmanr(
        df.loc[:, column],
        df.loc[:, "Total Deaths"],
        nan_policy="omit",
    )
    # if corr[1] <= 0.05:
    #     correlations_deaths_all.loc[0, column] = np.round(corr[0], 2)

    # correlations_deaths.loc[detailed_type, column] = list(
    #     [np.round(corr[0], 2), np.round(corr[1], 2)]
    # )

# # %%
# for detailed_type in detailed_types:
#     event_filter = df["eventtype_detailed"] == detailed_type
#     correlations_affected.loc[detailed_type, "Sample size"] = sum(event_filter)
#     for column in columns[0:6]:
#         try:
#             corr = scipy.stats.pearsonr(
#                 df.loc[event_filter, column], df.loc[event_filter, "Total Affected"]
#             )
#         except:
#             corr = list([np.nan, np.nan])

#         if corr[1] <= 0.05:
#             correlations_affected.loc[detailed_type, column] = np.round(corr[0], 2)

#     # correlations_deaths.loc[detailed_type, column] = list(
#     #     [np.round(corr[0], 2), np.round(corr[1], 2)]
#     # )


# %%
df_fl = df[df["eventtype_detailed"] == "fl"]
df_ls = df[df["eventtype_detailed"] == "ls"]
df_fl_ls = df[df["eventtype_detailed"] == "fl,ls"]

# %%
regr_fl = sm.OLS(
    df_fl["Total Deaths"],
    df_fl[["Population Count", "GDP per Capita PPP", "Intensity_fl"]],
).fit()

# %%
regr_ls = sm.OLS(
    df_ls["Total Deaths"],
    df_ls[["Population Count", "GDP per Capita PPP", "Intensity_ls"]],
).fit()
regr_fl_ls = sm.OLS(
    df_fl_ls["Total Deaths"],
    df_fl_ls[
        ["Population Count", "GDP per Capita PPP", "Intensity_fl", "Intensity_ls"]
    ],
).fit()

# %%
