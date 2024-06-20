###
# This file analysis the preprocessed EMDAT data

# %%
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# %% Constants
min_overlap_thres = 1
max_time_lag = 30

# %%
df = pd.read_csv(
    "data/df_single_and_pair_impacts_"
    + str(min_overlap_thres)
    + "_"
    + str(max_time_lag)
    + ".csv",
    sep=";",
)


# %%
impact_dam = "Total Damages 1"
impact_aff = "Total Affected 1"
impact_dea = "Total Deaths 1"

single_event_counts_dam = (
    df.dropna(subset=impact_dam)
    .loc[:, ["Hazard 1"]]
    .value_counts()
    .rename(index="Total Damages")
)
single_event_counts_aff = (
    df.dropna(subset=impact_aff)
    .loc[:, ["Hazard 1"]]
    .value_counts()
    .rename(index="Total Affected")
)
single_event_counts_dea = (
    df.dropna(subset=impact_dea)
    .loc[:, ["Hazard 1"]]
    .value_counts()
    .rename(index="Total Deaths")
)
# %%
single_event_counts = pd.concat(
    [single_event_counts_dam, single_event_counts_aff, single_event_counts_dea], axis=1
)
single_event_counts.to_csv(
    "data/single_events_data_availability_"
    + str(min_overlap_thres)
    + "_"
    + str(max_time_lag)
    + ".csv"
)


# %%
impact_dam = "Total Damages 2"
impact_aff = "Total Affected 2"
impact_dea = "Total Deaths 2"

second_event_counts_dam = (
    df.dropna(subset=impact_dam)
    .loc[:, ["Hazard 2"]]
    .value_counts()
    .rename(index="Total Damages")
)
second_event_counts_aff = (
    df.dropna(subset=impact_aff)
    .loc[:, ["Hazard 2"]]
    .value_counts()
    .rename(index="Total Affected")
)
second_event_counts_dea = (
    df.dropna(subset=impact_dea)
    .loc[:, ["Hazard 2"]]
    .value_counts()
    .rename(index="Total Deaths")
)
# %%
second_event_counts = pd.concat(
    [second_event_counts_dam, second_event_counts_aff, second_event_counts_dea], axis=1
)
# second_event_counts.to_csv("data/second_events_data_availability.csv")

# %%
impact_dam = "Total Damages 12"
impact_aff = "Total Affected 12"
impact_dea = "Total Deaths 12"

double_event_counts_dam = (
    df.dropna(subset=impact_dam)
    .loc[:, ["Hazard 1", "Hazard 2"]]
    .value_counts()
    .rename(index="Total Damages")
)
double_event_counts_aff = (
    df.dropna(subset=impact_aff)
    .loc[:, ["Hazard 1", "Hazard 2"]]
    .value_counts()
    .rename(index="Total Affected")
)
double_event_counts_dea = (
    df.dropna(subset=impact_dea)
    .loc[:, ["Hazard 1", "Hazard 2"]]
    .value_counts()
    .rename(index="Total Deaths")
)
# %%
double_event_counts = pd.concat(
    [double_event_counts_dam, double_event_counts_aff, double_event_counts_dea], axis=1
)
double_event_counts.to_csv(
    "data/double_events_data_availability_"
    + str(min_overlap_thres)
    + "_"
    + str(max_time_lag)
    + ".csv"
)

# %%
