# %% Imports
import pandas as pd
import itertools
import json


FIRST_YEAR = 2000
LAST_YEAR = 2018
PROCESSED_IMPACT_PATH_CSV = (
    "data/impact_" + str(FIRST_YEAR) + "_" + str(LAST_YEAR) + ".csv"
)
PROCESSED_EMDAT_PATH = "data/emdat_2000_2018.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_EMDAT_PATH).set_index("Dis No")
unique_records_sorted = df_emdat.sort_values(by="Start Date").index.values

# %%
min_overlap_thress = [0.25, 0.5, 0.75, 1]
max_time_lags = [0, 30, 91, 182, 365]


# %%
def get_influencing_records(record, record_pairs, df_emdat) -> list:
    filter_record = [record in ec for ec in record_pairs]
    overlapping_records = set(
        itertools.chain.from_iterable((itertools.compress(record_pairs, filter_record)))
    )
    if overlapping_records:
        overlapping_records.remove(record)

        # remove the ones later in time than record
        startdate_record = df_emdat.loc[record, "Start Date"]
    return [
        i
        for i in overlapping_records
        if df_emdat.loc[i, "Start Date"] <= startdate_record
    ]


# %%
for min_overlap_thres in min_overlap_thress:
    for max_time_lag in max_time_lags:

        filename = (
            "data/record_pairs_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv"
        )
        df = pd.read_csv(filename, sep=";")

        dict_all_records = dict()

        # for each record list all overlapping records
        record_pairs = list(
            df.loc[:, ["Record1", "Record2"]].itertuples(index=False, name=None)
        )

        for unique_record in unique_records_sorted:

            influencing_records = get_influencing_records(
                unique_record, record_pairs, df_emdat
            )

            loop_condition = True
            while loop_condition:
                influencing_records_temp = []
                influencing_records_updated = []
                for record_new in influencing_records:
                    influencing_records_temp = (
                        influencing_records_temp
                        + get_influencing_records(record_new, record_pairs, df_emdat)
                    )

                if unique_record in influencing_records_temp:
                    influencing_records_temp.remove(unique_record)

                influencing_records_updated = list(
                    set(influencing_records + influencing_records_temp)
                )

                if sorted(influencing_records) == sorted(influencing_records_updated):
                    loop_condition = False
                else:
                    influencing_records = influencing_records_updated

            all_records = influencing_records + [unique_record]

            # Sort records according to start date
            all_records_sorted = [
                e[0]
                for e in sorted(
                    [tuple([i, df_emdat.loc[i, "Start Date"]]) for i in all_records],
                    key=lambda a: a[1],
                )
            ]
            dict_all_records[unique_record] = json.dumps(all_records_sorted)

        df_event = pd.DataFrame.from_dict(
            dict_all_records, orient="index", columns=["Records"]
        )

        df_event["Records"] = df_event["Records"].apply(json.loads)

        df_event["No records"] = df_event["Records"].apply(len)

        for ix, row in df_event.iterrows():
            records = row.loc["Records"]
            hazards = []
            damages = []
            affected = []
            deaths = []
            for record in records:
                hazards = hazards + list(
                    df_emdat.loc[record, ["Hazard1", "Hazard2", "Hazard3"]]
                    .dropna()
                    .values
                )

            df_event.loc[ix, "Hazards"] = json.dumps(hazards)

        df_event["Hazards"] = df_event["Hazards"].apply(json.loads)
        df_event["No hazards"] = df_event["Hazards"].apply(len)

        df_event["Records"] = df_event["Records"].apply(json.dumps)
        df_event["Hazards"] = df_event["Hazards"].apply(json.dumps)

        df_event.to_csv(
            "data/df_events_"
            + str(min_overlap_thres)
            + "_"
            + str(max_time_lag)
            + ".csv",
            sep=";",
        )
