import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# relative path; ensure that the present script contains the data subdirectory
data_path = "data/barris.geojson"
gdf = gpd.read_file(data_path)

# compute barri areas, and append a column to gdf
gdf["area"] = gdf.area

if __name__ == "__main__":
    # geopandas dataframes have (primitive) built-in plotting functionality
    # map barri area to color
    gdf.plot("area", legend=True)
    plt.show()
