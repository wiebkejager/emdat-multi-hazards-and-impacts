# %% Imports
import pandas as pd
import numpy as np
import json

# %%
PROCESSED_IMPACT_PATH_CSV = "impact_2000_2015.csv"

# %%
df_emdat = pd.read_csv(PROCESSED_IMPACT_PATH_CSV, sep=";").set_index("Dis No")
df_emdat[["Hazard1", "Hazard2", "Hazard3"]] = df_emdat[
    ["Hazard1", "Hazard2", "Hazard3"]
].fillna("")
# %%
df_overlaps = pd.read_csv("df_res.csv", sep=";", index_col=0)
df_overlaps.replace("[]", np.nan, inplace=True)
df_overlaps.dropna(inplace=True)

# %%
# Add column indicating event set
# df_emdat.loc[:, "eventtype_detailed_unsrt"] = df_emdat[
#     ["Hazard1", "Hazard2", "Hazard3"]
# ].apply(lambda x: ",".join(list(x.dropna())), axis=1)

# Drop rows with more than 2 Hazards
# df_emdat = df_emdat.loc[df_emdat.loc[:, "Hazard3"].isna()]

# %%

# for ix, row in df_overlaps.iterrows():
#     for jx in json.loads(row["Overlapping events"]):
#         # Check if same event reported across different countries and merge
#         time_check = (
#             df_emdat.loc[ix, "Start Date"] == df_emdat.loc[jx, "Start Date"]
#         ) & (df_emdat.loc[ix, "End Date"] == df_emdat.loc[jx, "End Date"])
#         hazard_check = df_emdat.loc[ix, "Hazard1"] == df_emdat.loc[ix, "Hazard1"]
#         if time_check & hazard_check:
#             foo = 2
#         else:
#             print(ix)
#             print(jx)
#             foo = 2
# identify first and second hazard
# if both single hazards

# df_emdat.loc[ix, :]

# Merge events that are


# %%
cols = [
    "Dis No 1",
    "Dis No 2",
    "Hazard 1",
    "Hazard 2",
    "Start Date 1",
    "End Date 1",
    "Start Date 2",
    "End Date 2",
    "Country 1",
    "Country 2",
    "Magnitude 1",
    "Magnitude 2",
    "Total Deaths 1",
    "Total Deaths 2",
    "Total Deaths 12",
    "Total Affected 1",
    "Total Affected 2",
    "Total Affected 12",
    "Total Damages 1",
    "Total Damages 2",
    "Total Damages 12",
]

df = pd.DataFrame(
    columns=cols,
)

# %%
for ix, row in df_emdat.iterrows():
    # disaster does not have spatial overlap
    if ix not in df_overlaps.index:
        if row["Hazard3"] == "":
            new_row = pd.DataFrame(
                [
                    [
                        ix,
                        np.nan,
                        row["Hazard1"],
                        row["Hazard2"],
                        row["Start Date"],
                        row["End Date"],
                        np.nan,
                        np.nan,
                        row["Country"],
                        np.nan,
                        row["Dis Mag Value"],
                        np.nan,
                        np.nan,
                        np.nan,
                        np.nan,
                        np.nan,
                        np.nan,
                        np.nan,
                        np.nan,
                        np.nan,
                        np.nan,
                    ]
                ],
                columns=cols,
            )
            # and is single hazard
            if row["Hazard2"] == "":
                new_row["Total Deaths 1"] = row["Total Deaths"]
                new_row["Total Affected 1"] = row["Total Affected"]
                new_row["Total Damages 1"] = row["Total Damages, Adjusted ('000 US$')"]
            # and is double hazard
            else:
                new_row["Country 2"] = row["Country"]
                new_row["Total Deaths 12"] = row["Total Deaths"]
                new_row["Total Affected 12"] = row["Total Affected"]
                new_row["Total Damages 12"] = row["Total Damages, Adjusted ('000 US$')"]
            df = pd.concat([df, new_row], ignore_index=True)
    # disaster has spatial overlap and is single hazard:
    elif (row["Hazard2"] == "") & (row["Hazard3"] == ""):
        disastersi = [ix] + json.loads(df_overlaps.loc[ix, "Overlapping events"])
        df_tempi = df_emdat.loc[disastersi][["Start Date", "End Date"]].sort_values(
            by="Start Date"
        )
        jx = df_tempi.index[0]
        # # if 1st in overlapping hazards -> add to dataframe as H1
        # if ix == df_tempi.index[0]:
        #     new_row = pd.DataFrame(
        #         [
        #             [
        #                 ix,
        #                 np.nan,
        #                 row["Hazard1"],
        #                 np.nan,
        #                 row["Start Date"],
        #                 row["End Date"],
        #                 np.nan,
        #                 np.nan,
        #                 row["Country"],
        #                 np.nan,
        #                 row["Dis Mag Value"],
        #                 np.nan,
        #                 row["Total Deaths"],
        #                 np.nan,
        #                 np.nan,
        #                 row["Total Affected"],
        #                 np.nan,
        #                 np.nan,
        #                 row["Total Damages, Adjusted ('000 US$')"],
        #                 np.nan,
        #                 np.nan,
        #             ]
        #         ],
        #         columns=cols,
        #     )
        #     df = pd.concat([df, new_row], ignore_index=True)
        if (
            (ix == df_tempi.index[1])
            & (df_emdat.loc[jx, "Hazard2"] == "")
            & (df_emdat.loc[jx, "Hazard3"] == "")
        ):  # if 2nd in overlapping hazards and 1st hazard is also single hazard-> add to dataframe as H2
            new_row = pd.DataFrame(
                [
                    [
                        np.nan,
                        ix,
                        np.nan,
                        row["Hazard1"],
                        np.nan,
                        np.nan,
                        row["Start Date"],
                        row["End Date"],
                        np.nan,
                        row["Country"],
                        np.nan,
                        row["Dis Mag Value"],
                        np.nan,
                        row["Total Deaths"],
                        np.nan,
                        np.nan,
                        row["Total Affected"],
                        np.nan,
                        np.nan,
                        row["Total Damages, Adjusted ('000 US$')"],
                        np.nan,
                    ]
                ],
                columns=cols,
            )
            if jx not in df_overlaps.index:
                continue
            # if 1st hazard has no other overlapping hazard before it add as H1 and add H1+H2
            disastersj = [jx] + json.loads(df_overlaps.loc[jx, "Overlapping events"])
            df_tempj = df_emdat.loc[disastersj][["Start Date", "End Date"]].sort_values(
                by="Start Date"
            )
            if jx == df_tempj.index[0]:
                new_row["Dis No 1"] = jx
                new_row["Hazard 1"] = df_emdat.loc[jx, "Hazard1"]
                new_row["Magnitude 1"] = df_emdat.loc[jx, "Dis Mag Value"]
                new_row["Start Date 1"] = df_emdat.loc[jx, "Start Date"]
                new_row["End Date 1"] = df_emdat.loc[jx, "End Date"]
                new_row["Country 1"] = df_emdat.loc[jx, "Country"]
                new_row["Total Deaths 1"] = df_emdat.loc[jx, "Total Deaths"]
                new_row["Total Affected 1"] = df_emdat.loc[jx, "Total Affected"]
                new_row["Total Damages 1"] = df_emdat.loc[
                    jx, "Total Damages, Adjusted ('000 US$')"
                ]
                new_row["Total Deaths 12"] = (
                    new_row["Total Deaths 1"] + new_row["Total Deaths 2"]
                )
                new_row["Total Affected 12"] = (
                    new_row["Total Affected 1"] + new_row["Total Affected 2"]
                )
                new_row["Total Damages 12"] = (
                    new_row["Total Damages 1"] + new_row["Total Damages 2"]
                )

            df = pd.concat([df, new_row], ignore_index=True)

    else:
        continue

# %%
df.to_csv("df_impacts.csv", sep=";", index=False)

# %%
