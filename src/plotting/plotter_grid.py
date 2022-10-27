"""
This file is meant to take the clustered and processed output of the seaweed model
and make the appropriate plots
"""
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import geoplot as gplt
from shapely.geometry import Point
# plt.style.use("https://raw.githubusercontent.com/allfed/ALLFED-matplotlib-style-sheet/main/ALLFED.mplstyle")


def cluster_timeseries_only_growth(growth_df):
    """
    Plots the clusters that were found in postprocessing
    The plot is seperated by clusters and the median growth rate is plotted
    """
    fig, axes = plt.subplots(
        nrows=3, ncols=2, sharey=True, sharex=True, figsize=(15, 15)
    )

    axes = axes.flatten()
    for cluster, cluster_df in growth_df.groupby("cluster"):
        del cluster_df["cluster"]
        ax = axes[cluster]
        cluster_df.transpose().plot(ax=ax, color="black", legend=False, alpha=0.1)
        # Plot it two times, so the line has a edgecolor
        cluster_df.median().transpose().plot(
            ax=ax, color="black", legend=False, linewidth=4, alpha=0.9)
        cluster_df.median().transpose().plot(
            ax=ax, color="green", legend=False, linewidth=3, alpha=0.9)
        ax.set_ylabel("Fraction Optimal")
        ax.set_xlabel("Months since war")
        ax.set_title("Cluster: " + str(cluster) + ", n: " + str(cluster_df.shape[0]))
    plt.savefig(
        "results" + os.sep + "grid" + os.sep + "cluster_timeseries.png",
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()


def cluster_spatial(growth_df, global_or_US):
    """
    Creates a spatial plot of the clusters
    """
    global_map = gpd.read_file(
        "data/geospatial_information/Countries/ne_50m_admin_0_countries.shp"
    )
    growth_df.set_crs(epsg=4326, inplace=True)
    growth_df.to_crs(global_map.crs, inplace=True)
    growth_df["cluster"] = growth_df["cluster"].astype(str)
    ax = gplt.voronoi(growth_df, hue="cluster", legend=True, linewidth=0.3)
    fig = plt.gcf()
    fig.set_size_inches(15, 15)
    global_map.plot(ax=ax, color="white", edgecolor="black")
    if global_or_US == "US":
        ax.set_ylim(18, 55)
        ax.set_xlim(-130, -65)
    plt.savefig(
        "results" + os.sep + "grid" + os.sep + "cluster_spatial.png",
        dpi=200,
        bbox_inches="tight",
    )


def prepare_geometry(growth_df):
    """
    Prepares the geometry for the growth_df. For some reason the spatial data has
    a longitude that is 0-360 instead of -180 to 180. This function converts it to
    the latter
    """
    growth_df["latlon"] = growth_df.index
    growth_df["latitude"] = growth_df["latlon"].str[0]
    growth_df["longitude"] = growth_df["latlon"].str[1]
    growth_df["longitude"] = growth_df[growth_df["longitude"] > 180]["longitude"] - 360
    growth_df["geometry"] = growth_df[["longitude", "latitude"]].apply(tuple, axis=1)
    growth_df["geometry"] = growth_df["geometry"].apply(Point)
    growth_df = growth_df[["cluster", "geometry"]]
    growth_df = gpd.GeoDataFrame(growth_df)
    return growth_df


def cluster_timeseries_all_parameters(parameters):
    """
    Plots line plots for all clusters and all parameters
    Arguments:
        parameters: a dictionary of dataframes of all parameters
    Returns: 
        None, but saves the plot
    """
    fig, axes = plt.subplots(
        nrows=5, ncols=5, sharey=True, sharex=True, figsize=(20, 20)
    )
    i = 0
    for parameter, parameter_df in parameters.items():
        j = 0
        for cluster, cluster_df in parameter_df.groupby("cluster"):
            del cluster_df["cluster"]
            ax = axes[i, j]
            cluster_df.transpose().plot(ax=ax, color="black", legend=False, alpha=0.03)
            # Plot it two times, so the line has a edgecolor
            cluster_df.median().transpose().plot(
                ax=ax, color="black", legend=False, linewidth=5, alpha=0.9)
            cluster_df.median().transpose().plot(
                ax=ax, color="green", legend=False, linewidth=4, alpha=0.9)

            ax.set_ylabel(parameter) 
            ax.set_xlabel("Months since war")
            if i == 0:
                ax.set_title("Cluster: " + str(cluster) + ", n: " + str(cluster_df.shape[0]))
            j += 1
        i += 1
    plt.savefig(
        "results" + os.sep + "grid" + os.sep + "cluster_timeseries_all_param.png",
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

if __name__ == "__main__":
    # Either calculate for the whole world or just the US
    global_or_US = "US"
    growth_df = gpd.GeoDataFrame(
        pd.read_pickle(
            "data" + os.sep + "interim_results" + os.sep
            + "seaweed_growth_rate_clustered_" + global_or_US + ".pkl"
        )
    )
    cluster_timeseries_only_growth(growth_df)
    growth_df = prepare_geometry(growth_df)
    cluster_spatial(growth_df, global_or_US)
    parameters = {}
    for parameter in  ["salinity_factor", "nutrient_factor",
        "illumination_factor", "temp_factor", "seaweed_growth_rate"]:
        parameters[parameter] = pd.DataFrame(
            pd.read_pickle(
                "data" + os.sep + "interim_results" + os.sep
                + parameter + "_clustered_" + global_or_US + ".pkl"
            )
        )
    cluster_timeseries_all_parameters(parameters)

