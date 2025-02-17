"""
This file is meant to take the clustered and processed output of the seaweed model
and make the appropriate plots
"""
import os

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

from src.processing import read_files as rf
from src.utilities import prepare_geometry, weighted_quantile

plt.style.use(
    "https://raw.githubusercontent.com/allfed/ALLFED-matplotlib-style-sheet/main/ALLFED.mplstyle"
)


def cluster_spatial(growth_df, global_or_country, scenario, admin_1=False):
    """
    Creates a spatial plot of the clusters
    Arguments:
        growth_df: a dataframe of the growth rate
        global_or_country: a string of either "global" or "US" that indicates the scale
    Returns:
        None, but saves the plot
    """
    # Define the colors you want to use
    # Define a list of three colors that starts with #3A913F and gets 30 % lighter with each step
    colors = ["#95c091", "#dbf2ff", "#3A913F"]
    # Create the colormap using the colors and the position values
    custom_map = LinearSegmentedColormap.from_list("custom", colors, N=len(colors))

    print("Plotting cluster spatial")
    growth_df = growth_df.loc[:, ["cluster", "geometry"]]
    if admin_1:
        global_map_admin_1 = gpd.read_file(
            "data/geospatial_information/Countries_Admin_1/ne_50m_admin_1_states_provinces.shp"
        )
    global_map = gpd.read_file(
            "data/geospatial_information/Countries/ne_50m_admin_0_countries.shp"
        )
    growth_df.set_crs(epsg=4326, inplace=True)
    growth_df.to_crs(global_map.crs, inplace=True)
    growth_df["cluster"] = growth_df["cluster"].astype(str)
    ax = growth_df.plot(column="cluster", legend=True, cmap=custom_map, marker='s', markersize=85)
    fig = plt.gcf()
    fig.set_size_inches(12, 12)
    global_map.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.2)
    if admin_1:
        global_map_admin_1.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.2)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.get_legend().set_title("Cluster")
    if global_or_country == "US":
        ax.set_ylim(18, 55)
        ax.set_xlim(-130, -65)
    elif global_or_country == "AUS":
        ax.set_ylim(-47, -10)
        ax.set_xlim(105, 180)
    else:
        ax.set_ylim(-75, 85)
        ax.set_xlim(-180, 180)
    plt.savefig(
        "results"
        + os.sep
        + "grid"
        + os.sep
        + scenario
        + os.sep
        + "cluster_spatial_"
        + global_or_country
        + ".png",
        dpi=350,
        bbox_inches="tight",
    )


def growth_rate_spatial_by_year(growth_df, global_or_country, scenario, optimal_growth_rate):
    """
    Plots the growth rate by year. This includes the first
    three months without nuclear war, in the case of the first year
    Arguments:
        growth_df: a dataframe of the growth rate
    Returns:
        None, but saves the plot
    """
    print("Plotting growth rate by year")
    global_map = gpd.read_file(
        "data/geospatial_information/Countries/ne_50m_admin_0_countries.shp"
    )
    for year, i in enumerate(np.arange(-4, len(growth_df.columns) - 10, 12)):
        # Calculate the mean growth rate per year
        growth_df_year = growth_df.loc[:, i + 1 : i + 12]
        growth_df_year = growth_df_year.mean(axis=1)
        growth_df_year = growth_df_year.to_frame()
        growth_df_year.columns = ["growth_rate"]
        # Multiply it by optimal_growth_rate to get the actual growth rate
        growth_df_year["growth_rate"] = (
            growth_df_year["growth_rate"] * optimal_growth_rate
        )
        # Make it a geodataframe
        growth_df_year["geometry"] = growth_df["geometry"]
        growth_df_year = gpd.GeoDataFrame(growth_df_year)
        growth_df_year.set_crs(epsg=4326, inplace=True)
        growth_df_year.to_crs(global_map.crs, inplace=True)
        # Plot it
        ax = growth_df_year.plot(
            column="growth_rate",
            legend=True,
            cmap="viridis",
            marker='s',
            markersize=85,
            vmin=0,
            vmax=optimal_growth_rate,
            legend_kwds={
                "label": "Mean Daily Growth Rate [%]",
                "orientation": "vertical",
            },
        )
        global_map.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.2)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title("Year " + str(year + 1))
        if global_or_country == "US":
            ax.set_ylim(18, 55)
            ax.set_xlim(-130, -65)
        elif global_or_country == "AUS":
            ax.set_ylim(-47, -10)
            ax.set_xlim(105, 180)
        else:
            ax.set_ylim(-75, 85)
            ax.set_xlim(-180, 180)
        plt.savefig(
            "results"
            + os.sep
            + "grid"
            + os.sep
            + scenario
            + os.sep
            + "growth_rate_spatial_year_"
            + str(year + 1)
            + "_"
            + global_or_country
            + ".png",
            dpi=350,
            bbox_inches="tight",
        )


def cluster_timeseries_all_parameters_q_lines(
    parameters, global_or_country, scenario, areas
):
    """
    Plots line plots for all clusters and all parameters
    Arguments:
        parameters: a dictionary of dataframes of all parameters
    Returns:
        None, but saves the plot
    """
    print("Plotting cluster timeseries with q lines")
    # This is slightly larger than the actual area of the ocean due to the way the grid
    # is structured
    total_ocean_area = 361140210.2
    # Make the labels more clear
    parameter_names = {
        "salinity_factor": "Salinity Factor",
        "nutrient_factor": "Nutrient Factor",
        "illumination_factor": "Illumination Factor",
        "temp_factor": "Temperature Factor",
        "seaweed_growth_rate": "Total Growth Factor",
    }
    num_clusters = {"global": 3, "US": 4, "AUS": 2}
    clusters = num_clusters[global_or_country]
    fig, axes = plt.subplots(
        nrows=5, ncols=clusters, sharey=True, sharex=True, figsize=(12, 12)
    )
    i = 0
    # Iterate over all parameters and cluster to make all the subplots
    for parameter, parameter_df in parameters.items():
        j = 0
        for cluster, cluster_df in parameter_df.groupby("cluster"):
            # Combine area and cluster into one dataframe, merge by index
            # Reset the index, so we can join on column instead of index
            areas_reset = areas.reset_index()
            cluster_df = cluster_df.reset_index()
            # ROund the level and lat lon values to 4 decimals to make sure they match
            # level just refers to the level of the multi index, but contains the same
            # information as the lat lon
            cluster_df["level_0"] = cluster_df["level_0"].round(4)
            cluster_df["level_1"] = cluster_df["level_1"].round(4)
            areas_reset["TLAT"] = areas_reset["TLAT"].round(4)
            areas_reset["TLONG"] = areas_reset["TLONG"].round(4)
            cluster_df = pd.merge(
                cluster_df,
                areas_reset,
                left_on=["level_0", "level_1"],
                right_on=["TLAT", "TLONG"],
            )
            # Calculate the area
            cluster_area = cluster_df["TAREA"].sum()
            # Remove the columsn we don't need anymore
            area_weights = cluster_df["TAREA"]
            cluster_df = cluster_df.drop(
                columns=["cluster", "TLAT", "TLONG", "level_0", "level_1", "TAREA"]
            )
            ax = axes[i, j]
            for q in np.arange(0.1, 0.6, 0.1):
                # Calculate the quantiles for each months, weighted by area
                q_up = cluster_df.apply(weighted_quantile, args=(area_weights, 1 - q))
                q_down = cluster_df.apply(weighted_quantile, args=(area_weights, q))
                # Transpose the dataframes so that the index is the month
                q_up = q_up.transpose()
                q_down = q_down.transpose()
                # Make the quantiles into a series, so that we can plot them
                q_up = pd.Series(q_up.iloc[:, 0])
                q_down = pd.Series(q_down.iloc[:, 0])
                ax.fill_between(
                    x=q_up.index.astype(float),
                    y1=q_down,
                    y2=q_up,
                    color="#3A913F",
                    # Make the color more transparent with each quantile
                    alpha=q * 2,
                )
            ax.plot(cluster_df.median(), color="black")
            # Labels
            if j == 0:
                ax.set_ylabel(parameter_names[parameter])
            if i == 4:
                ax.set_xlabel("Months since nuclear war")
            if i == 0 and global_or_country == "global":
                ax.set_title(
                    "Cluster: "
                    + str(cluster)
                    + ", "
                    + str(int(round(cluster_area / total_ocean_area * 100, 0)))
                    + "% of Ocean Area"
                )
            # Add a legend
            if j == 0 and i == 0:
                # Create the legend
                patches_list = []
                patches_list.append(mpatches.Patch(color="black", label="Median"))
                patches_list.append(
                    mpatches.Patch(color="#3A913F", label="Q40 - Q60", alpha=0.8)
                )
                patches_list.append(
                    mpatches.Patch(color="#3A913F", label="Q30 - Q70", alpha=0.6)
                )
                patches_list.append(
                    mpatches.Patch(color="#3A913F", label="Q20 - Q80", alpha=0.4)
                )
                patches_list.append(
                    mpatches.Patch(color="#3A913F", label="Q10 - Q90", alpha=0.2)
                )
                ax.legend(handles=patches_list)
            j += 1
        i += 1
    # Add the subplot labels
    for i, ax in enumerate(axes.flat):
        ax.text(
            0,
            1,
            f"{chr(97+i)})",
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            horizontalalignment="left",
            color="black",
            alpha=0.9,
            backgroundcolor="white",
        )
    plt.savefig(
        "results"
        + os.sep
        + "grid"
        + os.sep
        + scenario
        + os.sep
        + "cluster_timeseries_all_param_q_lines_"
        + global_or_country
        + ".png",
        dpi=350,
        bbox_inches="tight",
    )
    plt.close()


def compare_nw_scenarios(areas, optimal_growth_rate):
    """
    Compares the results of the nuclear war scenarios as weigthed median
    Arguments:
        areas: A dataframe containing the area of each grid cell
        eez: A eez around coastlines to only use those areas
    Returns:
        None
    """
    print("Starting the NW comparison plots")
    # A dictionary of seven colors, starting with #3A913F for the scenarios
    colors = {
        "150 Tg": "#3A913F",
        "47 Tg": "#5DAF5D",
        "37 Tg": "#7FC17F",
        "27 Tg": "#A1DCA1",
        "16 Tg": "#C3F5C3",
        "5 Tg": "#E6FFE6",
        "Control": "#95c091",
    }
    # have a list that is used to save the scenario results
    median_weighted_list = []
    for scenario in [str(i) + "tg" for i in [150, 47, 37, 27, 16, 5]] + ["control"]:
        print("Starting scenario: " + scenario)
        # Read the data
        growth_df_scenario = pd.read_pickle(
            "data"
            + os.sep
            + "interim_data"
            + os.sep
            + scenario
            + os.sep
            + "seaweed_growth_rate_global.pkl"
        )
        # Reset the index, so we can join on column instead of
        areas_reset = areas.reset_index()
        growth_df_scenario = growth_df_scenario.reset_index()
        # Only use those grid cells that are between -45 and 45 degrees latitude
        # This is because the areas above and below have 0 growth either way
        growth_df_scenario = growth_df_scenario[growth_df_scenario["level_0"] > -45]
        growth_df_scenario = growth_df_scenario[growth_df_scenario["level_0"] < 45]
        # Combine area and cluster into one dataframe, merge by index
        # Round the level and lat lon values to 4 decimals to make sure they match
        # level just refers to the level of the multi index, but contains the same
        # information as the lat lon
        growth_df_scenario["level_0"] = growth_df_scenario["level_0"].round(4)
        growth_df_scenario["level_1"] = growth_df_scenario["level_1"].round(4)
        areas_reset["TLAT"] = areas_reset["TLAT"].round(4)
        areas_reset["TLONG"] = areas_reset["TLONG"].round(4)
        # Merge the dataframes, so that we have the area for each grid cell
        # And remove the grid cells without data.
        growth_df_scenario = pd.merge(
            growth_df_scenario,
            areas_reset,
            left_on=["level_0", "level_1"],
            right_on=["TLAT", "TLONG"],
        )
        # Remove the columsn we don't need anymore
        areas_reset = growth_df_scenario["TAREA"]
        # Drop additional geospacial columns if we used a eez
        growth_df_scenario = growth_df_scenario.drop(
            columns=["TLAT", "TLONG", "level_0", "level_1", "TAREA"]
        )
        # Calculate the weighted median
        median_weighted = growth_df_scenario.apply(
            weighted_quantile, args=(areas_reset, 0.5)
        ).transpose()
        # Save it in a list
        median_weighted_list.append(median_weighted.values)
    all_medians = pd.DataFrame(
        np.concatenate(median_weighted_list, axis=1),
        columns=[
            "150 Tg",
            "47 Tg",
            "37 Tg",
            "27 Tg",
            "16 Tg",
            "5 Tg",
            "Control",
        ],
    )
    # Remove the first three months, because they are before the nuclear war
    all_medians = all_medians.iloc[3:]
    # Multiply the values in the columns by optimal_growth_rate, which is the maximum growth rate
    all_medians = all_medians * optimal_growth_rate
    # Calculate the median for each year
    all_medians = all_medians.groupby(all_medians.index // 12).median()
    # Add one to the years, so that the first year is 1
    all_medians.index = all_medians.index + 1
    # plot them all in the same subplot as bar plots
    ax = all_medians.plot.bar(color=colors, edgecolor="black", linewidth=0.1, legend=False)
    # Create a custom legend for the plot with 7 columns
    custom_lines = [
        Line2D([0], [0], color=colors["150 Tg"], lw=4),
        Line2D([0], [0], color=colors["47 Tg"], lw=4),
        Line2D([0], [0], color=colors["37 Tg"], lw=4),
        Line2D([0], [0], color=colors["27 Tg"], lw=4),
        Line2D([0], [0], color=colors["16 Tg"], lw=4),
        Line2D([0], [0], color=colors["5 Tg"], lw=4),
        Line2D([0], [0], color=colors["Control"], lw=4),
    ]
    ax.legend(
        custom_lines,
        ["150 Tg", "47 Tg", "37 Tg", "27 Tg", "16 Tg", "5 Tg", "Control"],
        ncol=7,
        fontsize=8,
    )
    # Make it nicer
    ax.set_xlabel("Year after Nuclear War")
    ax.set_ylabel("Median Daily Growth Rate [%]")
    # Rotate the xtick labels so they are parallel to the x axis
    plt.xticks(rotation=0)
    # Remove the x grid
    ax.xaxis.grid(False)
    plt.savefig(
        "results" + os.sep + "grid" + os.sep + "comparing_nw_scenarios.png",
        dpi=350,
        bbox_inches="tight",
    )


def compare_nutrient_subfactors(nitrate, ammonium, phosphate, scenario, areas):
    """
    Takes the weighted average of the nutrient subfactors globally and plots them
    in the same plot to be able to compare them.
    Arguments:
        nitrate: The nitrate subfactor
        ammonium: The ammonium subfactor
        phosphate: The phosphate subfactor
        scenario: The scenario to plot
        areas: The areas of the grid cells
    Returns:
        None
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # a list of 3 very distinct colors
    colors = ["#3a913f", "#dc582a", "#75787b"]
    labels = ["Nitrate Subfactor", "Ammonium Subfactor", "Phosphate Subfactor"]
    i = 0
    for nutrient in [nitrate, ammonium, phosphate]:
        # Reset the index, so we can join on column
        nutrient_reset = nutrient.reset_index()
        areas_reset = areas.reset_index()
        # Round the level and lat lon values to 4 decimals to make sure they match
        nutrient_reset["level_0"] = nutrient_reset["level_0"].round(4)
        nutrient_reset["level_1"] = nutrient_reset["level_1"].round(4)
        areas_reset["TLAT"] = areas_reset["TLAT"].round(4)
        areas_reset["TLONG"] = areas_reset["TLONG"].round(4)
        # Merge the dataframes, so that we have the area for each grid cell
        nutrient_merged = pd.merge(
            nutrient_reset,
            areas_reset,
            left_on=["level_0", "level_1"],
            right_on=["TLAT", "TLONG"],
        )
        # Only use the remaining cells
        areas_reset = nutrient_merged["TAREA"]
        # Remove the columsn we don't need anymore
        nutrient_merged = nutrient_merged.drop(
            columns=["TLAT", "TLONG", "level_0", "level_1", "TAREA", "cluster"]
        )
        # Calculate the weighted median
        median_weighted = nutrient_merged.apply(
            weighted_quantile, args=(areas_reset, 0.5)
        ).transpose()
        # Plot the median
        ax.plot(median_weighted, color="black", linewidth=2)
        ax.plot(median_weighted, label=labels[i], color=colors[i], linewidth=1.5)
        ax.set_ylim(0, 1)
        i += 1
    # Make it nicer
    ax.set_xlabel("Months since Nuclear War")
    ax.set_ylabel("Nutrient Subfactor")
    # save
    plt.legend()
    plt.savefig(
        "results"
        + os.sep
        + "grid"
        + os.sep
        + scenario
        + os.sep
        + "comparing_nutrient_subfactors.png",
        dpi=350,
        bbox_inches="tight",
    )


def plot(scenario, global_or_country, optimal_growth_rate, admin_1=False):
    """
    Runs the other functions to read the data and make the plots
    Arguments:
        scenario: The scenario to plot
        global_or_country: Whether to plot the global or a country scenario
        optimal_growth_rate: The maximum growth rate
    Returns:
        None
    """
    # Read the data
    # File with the areas of the grid cells
    areas = rf.read_area_file(
        "data" + os.sep + "geospatial_information" + os.sep + "grid", "area_grid.csv"
    )
    # File with the seaweed growth rate
    growth_df = gpd.GeoDataFrame(
        pd.read_pickle(
            "data"
            + os.sep
            + "interim_data"
            + os.sep
            + scenario
            + os.sep
            + "seaweed_growth_rate_clustered_"
            + global_or_country
            + ".pkl"
        )
    )
    # Add one to the cluster to make it start at 1
    growth_df["cluster"] = growth_df["cluster"] + 1
    # Make sure that each entry has a value
    num_nan = growth_df.isna().sum().sum()
    assert num_nan == 0, "The dataframe has {} nan".format(num_nan)
    # Fix the geometry
    growth_df = prepare_geometry(growth_df)
    # Make the spatial plots
    cluster_spatial(growth_df, global_or_country, scenario, admin_1)
    growth_rate_spatial_by_year(growth_df, global_or_country, scenario, optimal_growth_rate)
    # Read in the other parameters for the line plots
    parameters = {}
    parameter_names = [
        "salinity_factor",
        "nutrient_factor",
        "illumination_factor",
        "temp_factor",
        "seaweed_growth_rate",
        "nitrate_subfactor",
        "phosphate_subfactor",
        "ammonium_subfactor",
    ]
    # Read in the data to plot
    for parameter in parameter_names:
        parameters[parameter] = pd.DataFrame(
            pd.read_pickle(
                "data"
                + os.sep
                + "interim_data"
                + os.sep
                + scenario
                + os.sep
                + parameter
                + "_clustered_"
                + global_or_country
                + ".pkl"
            )
        )
        # Add one to the cluster
        parameters[parameter]["cluster"] = parameters[parameter]["cluster"] + 1
    # Plot the nutrient subfactors comparison
    compare_nutrient_subfactors(
        parameters["nitrate_subfactor"],
        parameters["ammonium_subfactor"],
        parameters["phosphate_subfactor"],
        scenario,
        areas,
    )
    # Remove the subfactors from the parameters, as they aren't the main parameters and not needed
    # for the line plot
    del parameters["nitrate_subfactor"]
    del parameters["ammonium_subfactor"]
    del parameters["phosphate_subfactor"]
    # Plot the timeseries that compares how the parameters change over time
    cluster_timeseries_all_parameters_q_lines(parameters, global_or_country, scenario, areas)


if __name__ == "__main__":
    optimal_growth_rate = 30  # %/day
    # Call this seperately, as it needs to access all scenarios
    # Compare the nuclear war scenarios
    areas = rf.read_area_file(
        "data" + os.sep + "geospatial_information" + os.sep + "grid", "area_grid.csv"
    )
    # This is done seperately, as it needs to access all scenarios
    compare_nw_scenarios(areas, optimal_growth_rate)
    # Create the US plots
    main("150tg", "US", optimal_growth_rate)
    # Iterate over all scenarios
    for scenario in [str(i) + "tg" for i in [150, 5, 16, 27, 37, 47]] + ["control"]:
        print("\nPreparing scenario: " + scenario)
        main(scenario, "global", optimal_growth_rate)
