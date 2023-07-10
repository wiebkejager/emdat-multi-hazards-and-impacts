# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import BinaryCrossentropy

# %% Define constants
PROCESSED_IMPACT_EXP_AND_VUL_PATH_CSV = "C:/Users/wja209/DATA/PROCESSED/impact_hazard_exposure_vulnerability_2000_2015_continuous.csv"

# %% Load impact data
df = pd.read_csv(PROCESSED_IMPACT_EXP_AND_VUL_PATH_CSV).set_index("Dis No")
df = df.dropna(subset=["Population Count", "GDP per Capita PPP"])

# %% Add column indicating single-hazard or multi-hazard
eventtypes = ["multi-hazard", "single-hazard"]
df.loc[:, "eventtype"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: eventtypes[0] if sum(x.isna()) <= 1 else eventtypes[1], axis=1
)
# Add column indicating single-hazard or multi-hazard
df.loc[:, "eventtype_detailed"] = df[["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)

df.loc[:, "eventtype_detailed"].value_counts()


# %%
# df.loc[:, "Duration"] = (
#     (
#         pd.to_datetime(df.loc[:, "End Date"]) - pd.to_datetime(df.loc[:, "Start Date"])
#     ).dt.total_seconds()
#     / 60
#     / 60
#     / 24
# )  # in days


# %%
vars = [
    "Total Deaths",
    "Intensity_fl",
    "Intensity_ew",
    "Duration",
]

sns.pairplot(
    df.loc[
        :,
        vars,
    ],
    diag_kind="kde",
)

df_ranks = df.copy()
df_ranks.loc[:, vars] = (
    df_ranks.loc[:, vars].rank() / df_ranks.loc[:, vars].rank().max()
)
sns.pairplot(df_ranks.loc[:, vars], diag_kind="hist")


# %% Correlations event types
correlations = pd.DataFrame(
    index=eventtypes,
    columns=vars[1 : len(vars)],
)

for eventtype in eventtypes:
    event_filter = df["eventtype"] == eventtype
    correlations.loc[eventtype, "Sample size"] = sum(event_filter)
    for var in vars[1 : len(vars)]:
        try:
            corr = stats.spearmanr(
                df.loc[event_filter, var],
                df.loc[event_filter, vars[0]],
                nan_policy="omit",
            )
        except:
            corr = list([np.nan, np.nan])

        if corr[1] <= 0.05:
            correlations.loc[eventtype, var] = np.round(corr[0], 2)

print(correlations)

# %%
vars = [
    "Total Affected",
    "Population Count",
    "GDP per Capita PPP",
    "Affected Area",
    "Duration",
    "Intensity_fl",
    "Intensity_eq",
    "Intensity_ls",
    "Intensity_ew",
]

# %% Correlations detailed event types
eventtypes_detailed = ["fl", "eq", "fl,ls", "ew", "fl, ls", "ls", "ew, fl"]

correlations = pd.DataFrame(
    index=eventtypes_detailed,
    columns=vars[1 : len(vars)],
)

for eventtype in eventtypes_detailed:
    event_filter = df["eventtype_detailed"] == eventtype
    correlations.loc[eventtype, "Sample size"] = sum(event_filter)
    for var in vars[1 : len(vars)]:
        try:
            corr = stats.spearmanr(
                df.loc[event_filter, var],
                df.loc[event_filter, vars[0]],
                nan_policy="omit",
            )
        except:
            corr = list([np.nan, np.nan])

        if corr[1] <= 0.05:
            correlations.loc[eventtype, var] = np.round(corr[0], 2)

print(correlations)


# %% Define training features and labels
vars = [
    "Total Affected",
    "Population Count",
    "GDP per Capita PPP",
    "Duration",
    "Intensity_fl",
    "Intensity_eq",
    "Intensity_dr",
    "Intensity_ts",
    "Intensity_vo",
    "Intensity_ls",
    "Intensity_hw",
    "Intensity_ew",
    "Intensity_cw",
    "eventtype_detailed",
]
train_features = df.loc[:, vars].dropna()
train_features = pd.get_dummies(
    train_features,
    columns=["eventtype_detailed"],
    prefix="",
    prefix_sep="",
    dtype=float,
)

train_labels = train_features.pop("Total Affected")
# multi_filter = train_features.loc[:, "multi-hazard"] == 1

# %% Random Forest Model
from sklearn.ensemble import RandomForestRegressor

# Instantiate model with 100 decision trees
rf = RandomForestRegressor(n_estimators=100, random_state=42)
# Train the model on training data
rf.fit(train_features, train_labels)

# Use the forest's predict method on the training data
predictions = rf.predict(train_features)

# Plot
ax = sns.scatterplot(x=train_labels.values, y=predictions)
ax.set(
    xlabel="True Total Affected",
    ylabel="Predicted Total Affected",
    xlim=(0, 2500000),
    ylim=(0, 2500000),
    # xscale="log",
    # yscale="log",
)
ax.axline((1, 1), (10**8, 10**8), color="r")

# %%
