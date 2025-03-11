# %% Imports
import pandas as pd
import json

# %% Constants
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"
min_overlap_thress = [0.5]  # [0, 0.25, 0.5, 0.75, 1]
max_time_lags = [91]  # [0, 30, 91, 182, 365]

# %% Load processed EM-DAT
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

# %% Attach impact metrics to multi-hazard event sets with different spatiotemporal overlap criteria
for min_overlap_thres in min_overlap_thress:
    for max_time_lag in max_time_lags:

        # Read file
        filename = (
            "data/df_events_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv"
        )
        df_events = pd.read_csv(filename, sep=";")

        # Drop useless column
        df_events.drop(df_events.columns[0], axis=1, inplace=True)
        # Sort records column to make looping faster
        df_events.sort_values(by="Records")
        # Convert string of records to list of records
        df_events["Records"] = df_events["Records"].apply(json.loads)
        # Create multi-hazard events set
        df_events_and_impacts = df_events.copy(deep=True)

        # Drop duplicates
        for ix, irow in df_events.iterrows():
            is_subset = False
            for jx, jrow in df_events.iterrows():
                # Check if chain is included in another chain
                if ix != jx:
                    is_subset = set(irow["Records"]).issubset(jrow["Records"])
                    # If chain is included in another chain drop from multi-hazard events df
                    if is_subset == True:
                        df_events_and_impacts.drop(ix, inplace=True)
                        break

        # Add impact metrics
        for ix, row in df_events_and_impacts.iterrows():
            deaths = 0
            affected = 0
            damage = 0
            for record in row["Records"]:
                deaths = (deaths + df_emdat.loc[record, "Total Deaths"]).sum()
                affected = (affected + df_emdat.loc[record, "Total Affected"]).sum()
                damage = (
                    damage + df_emdat.loc[record, "Total Damages, Adjusted ('000 US$')"]
                ).sum()
            df_events_and_impacts.loc[ix, "Total deaths"] = deaths
            df_events_and_impacts.loc[ix, "Total affected"] = affected
            df_events_and_impacts.loc[ix, "Total damages"] = damage

        # Add information on time lag and overlap for later analysis
        df_events_and_impacts.loc[:, "Time lag"] = max_time_lag
        df_events_and_impacts.loc[:, "Spatial overlap"] = min_overlap_thres

        # Save to file
        df_events_and_impacts.to_csv(
            "data/df_events_and_impacts"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv",
            sep=";",
            index=False,
        )
