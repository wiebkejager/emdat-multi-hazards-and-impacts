# %% Imports
import pandas as pd
import datetime
import json


df_s_t_overlapping_events = pd.read_csv(
    "data/df_s_t_overlapping_events.csv", sep=";", index_col=0
)
