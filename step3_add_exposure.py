# %% Imports
import geopandas as gpd
import rasterstats
import rasterio as rio

# %%
START_YEAR = 2000
END_YEAR = 2015
EXPOSURE_PATH_1 = "C:/Users/wja209/DATA/RAW/WorldPop/"
PROCESSED_IMPACT_AND_VUL_PATH = (
    "C:/Users/wja209/DATA/PROCESSED/impact_vulnerability_2000_2015.gpkg"
)
PROCESSED_IMPACT_EXP_AND_VUL_PATH = (
    "C:/Users/wja209/DATA/PROCESSED/impact_exposure_vulnerability_2000_2015.gpkg"
)

# %%
gdf_impact = gpd.read_file(PROCESSED_IMPACT_AND_VUL_PATH)

# %%
impact_years = gdf_impact["Start Date"].dt.year.dropna().unique()

# %% Add population count
for year in impact_years:
    print(year)
    EXPOSURE_PATH = EXPOSURE_PATH_1 + "ppp_" + str(int(year)) + "_1km_Aggregated.tif"
    ds_exp = rio.open(EXPOSURE_PATH)
    year_filter = gdf_impact["Start Date"].dt.year == year
    gdf_impact.loc[year_filter, "Population Count"] = [
        x["sum"]
        for x in rasterstats.zonal_stats(
            gdf_impact.loc[year_filter, "geometry"],
            ds_exp.read(1),
            nodata=ds_exp.nodata,
            affine=ds_exp.transform,
            stats="sum",
        )
    ]

# %% Save merged file
gdf_impact.to_file(PROCESSED_IMPACT_EXP_AND_VUL_PATH)

# %%
