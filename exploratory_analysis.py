#%% Imports
import pandas as pd

#%% Constants
EM_DAT_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/EM-DAT/emdat_public_2023_03_31_query_uid-n7b9hv-natural-sisasters.csv"
HAZ_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/MYRIAD-HESA example data/MYRIAD-HES_simple.csv"

#%% Load data
df_em_dat_raw = pd.read_csv(EM_DAT_PATH, delimiter= ';')

#%%
df_em_dat_raw["Start Date"] = pd.to_datetime(df_em_dat_raw[['Start Year', 'Start Month', 'Start Day']].rename(columns = {'Start Year':'year', 'Start Month': 'month', 'Start Day': 'day'}))
df_em_dat_raw["End Date"] = pd.to_datetime(df_em_dat_raw[['End Year', 'End Month', 'End Day']].rename(columns = {'End Year':'year', 'End Month': 'month', 'End Day': 'day'}))

# %%
df_em_dat = df_em_dat_raw[[
    "Start Date", 
    "End Date",
    "Total Affected",
    "Country", 
    "Latitude", 
    "Longitude",
    "Disaster Type", 
    "Associated Dis",
    "Associated Dis2"
]]

# %%
df_haz_raw = pd.read_csv(HAZ_PATH, delimiter= ',')

# %%
df_haz = df_haz_raw[[
    "starttime", 
    "endtime",
    "Hazard", 
    "Intensity",
    "Unit",
    "event",
    "minlon",
    "minlat",
    "maxlon",
    "maxlat"
]].rename(columns={
    "starttime": "Start Date", 
    "endtime": "End Date"
    })

# %%
