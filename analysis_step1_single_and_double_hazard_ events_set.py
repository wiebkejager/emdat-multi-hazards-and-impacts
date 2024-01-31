# %% Imports
import pandas as pd


# %% Constants
# %%
df = pd.read_csv(
    "data/df_impacts_of_single_and_pair_events.csv", sep=";", index_col=False
)

# %%
df_pivot = df.pivot_table(
    values="Type Event",
    index=["Continent 1"],
    columns=["Type Hazards"],
    aggfunc="count",
)
# %%
c = [
    "1st most frequent",
    "2nd most frequent",
    "3rd most frequent",
    "4th most frequent",
    "5th most frequent",
]
df_pivot_largest = df_pivot.apply(
    lambda x: pd.Series(pd.to_numeric(x).nlargest(5).index, index=c), axis=1
).reset_index()

# %%
