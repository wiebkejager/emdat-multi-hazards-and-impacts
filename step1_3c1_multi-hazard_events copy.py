# %% Imports
import pandas as pd
import json

# %% Constants
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"
min_overlap_thress = [0.75, 1]  # [0, 0.25, 0.5, 0.75, 1]
max_time_lags = [0, 30, 91, 182, 365]

# %% Load processed EM-DAT
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")

# %% Develop multi-hazard event sets with impact metrics for different spatiotemporal overlap criteria
for min_overlap_thres in min_overlap_thress:
    for max_time_lag in max_time_lags:

        if (min_overlap_thres == 0.75) & (max_time_lag <= 91):  # TAKE OUT
            continue

        # Read file
        filename = (
            "data/df_chain_" + str(min_overlap_thres) + "_" + str(max_time_lag) + ".csv"
        )
        df_chain = pd.read_csv(filename, sep=";")

        # Drop useless column
        df_chain.drop(df_chain.columns[0], axis=1, inplace=True)
        # Sort records column to make looping faster
        df_chain.sort_values(by="Events")
        # Convert string of events to list of events
        df_chain["Events"] = df_chain["Events"].apply(json.loads)
        # Create multi-hazard events set
        df_mh_events = df_chain.copy(deep=True)

        # Drop duplicates
        for ix, irow in df_chain.iterrows():
            is_subset = False
            for jx, jrow in df_chain.iterrows():
                # Check if chain is included in another chain
                if ix != jx:
                    is_subset = set(irow["Events"]).issubset(jrow["Events"])
                    # If chain is included in another chain drop from multi-hazard events df
                    if is_subset == True:
                        df_mh_events.drop(ix, inplace=True)
                        break

        # Add impact metrics
        for ix, row in df_mh_events.iterrows():
            deaths = 0
            affected = 0
            damage = 0
            for record in row["Events"]:
                deaths = (deaths + df_emdat.loc[record, "Total Deaths"]).sum()
                affected = (affected + df_emdat.loc[record, "Total Affected"]).sum()
                damage = (
                    damage + df_emdat.loc[record, "Total Damages, Adjusted ('000 US$')"]
                ).sum()
            df_mh_events.loc[ix, "Total deaths"] = deaths
            df_mh_events.loc[ix, "Total affected"] = affected
            df_mh_events.loc[ix, "Total damages"] = damage

        # Add information on time lag and overlap for later analysis
        df_mh_events.loc[:, "Time lag"] = max_time_lag
        df_mh_events.loc[:, "Spatial overlap"] = min_overlap_thres

        # Save to file
        df_mh_events.to_csv(
            "data/df_mh_events_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv",
            sep=";",
            index=False,
        )
