import pandas as pd
import geopandas as gpd
from shapely import wkt


def get_bs_sample_df(df: pd.DataFrame, haz: str) -> pd.DataFrame:
    filter = (
        df.loc[:, "eventtype_detailed"] == haz
    )  # get indices of data rows that correspond to hazard of interest
    df_filtered = df.loc[filter]  # get data rows that correspond to hazard
    n_bs = len(df_filtered)  # size of bootstrap sample
    df_new = df_filtered.sample(
        n_bs, replace=True
    )  # create bootstrap sample of size n_bs
    return df_new


# %%
def get_impact_mean(df_haz: pd.DataFrame, impact_var: str) -> float:
    impact_mean = df_haz[impact_var].mean()
    return impact_mean
