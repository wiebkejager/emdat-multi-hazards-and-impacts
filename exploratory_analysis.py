#%% Imports
import pandas as pd

#%% Constants
EM_DAT_PATH = "C:/Users/wja209/OneDrive - Vrije Universiteit Amsterdam/Research/Paper 1 - Ruoying/Data/EM-DAT/emdat_public_2023_03_31_query_uid-n7b9hv-natural-sisasters.csv"

#%% Load data
df_em_dat = pd.read_csv(EM_DAT_PATH, delimiter= ';')


# %%
df = df_em_dat