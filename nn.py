# %%
import pandas as pd
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import BinaryCrossentropy
import seaborn as sns
import numpy as np

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
hazards = ["fl", "ew", "ls", "eq"]

hazard_filter = (
    (df_all["Hazard1"].isin(hazards))
    & ((df_all["Hazard2"].isin(hazards)) | df_all["Hazard2"].isna())
    & ((df_all["Hazard3"].isin(hazards)) | df_all["Hazard3"].isna())
    & (df_all["Hazard1"] != df_all["Hazard2"])
)
df = df_all[hazard_filter]

# %%
df.loc[:, "eventtype_detailed"] = df.loc[:, ["Hazard1", "Hazard2", "Hazard3"]].apply(
    lambda x: ",".join(sorted(list(x.dropna()))), axis=1
)

df = pd.get_dummies(
    df, columns=["eventtype_detailed"], prefix="", prefix_sep="", dtype=float
)

# %%
df = df.drop(
    columns=[
        "Total Affected",
        # "Total Deaths",
        "Country",
        "ISO",
        "Continent",
        "Start Date",
        "End Date",
        "Hazard1",
        "Hazard2",
        "Hazard3",
        "Intensity_dr",
        "Intensity_ts",
        "Intensity_vo",
        "Intensity_hw",
        "Intensity_cw",
    ]
).dropna()


# %%
df["Total Deaths"] = df["Total Deaths"] + np.random.normal(0, 1, size=len(df))

# %%
foo_filter = df["GDP per Capita PPP"] >= 10000

# %% Drop extreme events
# df = df[
#     (df["Total Deaths"] < np.quantile(df["Total Deaths"], q=0.99))
#     & (df["Total Deaths"] > np.quantile(df["Total Deaths"], q=0.01))
# ]


# %%
numeric_features = df.drop(columns=["Total Deaths"])
target = df["Total Deaths"]

# %%
vars = [
    "GDP per Capita PPP",
    "Population Count",
    "Intensity_eq",
    "Intensity_fl",
    "Intensity_ls",
    "Intensity_ew",
    "Total Deaths",
]
sns.pairplot(
    df.loc[
        ~foo_filter,
        vars,
    ].replace(0, np.nan),
    diag_kind="kde",
)

# %%
df_ranks = df.replace(0, np.nan).copy()
df_ranks.loc[:, vars] = (
    df_ranks.loc[:, vars].rank() / df_ranks.loc[:, vars].rank().max()
)
sns.pairplot(df_ranks.loc[:, vars], diag_kind="hist")

# %%
train_features = df.copy()
train_labels = train_features.pop("Total Deaths")


# %%
normalizer = tf.keras.layers.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))

# %% Linear regression with multiple inputs
model = Sequential(
    [
        normalizer,
        Dense(units=len(train_features.columns), activation="relu"),
        Dense(units=len(train_features.columns), activation="relu"),
        Dense(units=len(train_features.columns), activation="relu"),
        Dense(units=len(train_features.columns), activation="relu"),
        Dense(units=len(train_features.columns), activation="relu"),
        Dense(units=len(train_features.columns), activation="relu"),
        Dense(units=1, activation="relu"),
    ]
)

model.compile(loss=BinaryCrossentropy())
model.fit(train_features, target, epochs=100)

# Quick evaluation
total_death_predicted = model.predict(np.array(train_features))
sns.scatterplot(x=target.values, y=total_death_predicted.squeeze())

# %%
