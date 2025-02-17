"""
This file takes the output of the seaweed model and does time series analysis with it
"""
import os
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tslearn.clustering import TimeSeriesKMeans
from tslearn.utils import to_time_series_dataset

from src.model.seaweed_model import SeaweedModel

# Import the ALLFED stle
plt.style.use(
    "https://raw.githubusercontent.com/allfed/ALLFED-matplotlib-style-sheet/main/ALLFED.mplstyle"
)

# Make sure that everything is reproducible
random.seed(42)
np.random.seed(42)


def get_parameter_dataframe(parameter, path, file):
    """
    Initializes the seaweed model and returns the dataframe with the parameter
    for all the grid sections
    Arguments:
        parameter: the parameter to construct the dataframe for
        path: The path to the file
        file: The file name
    Returns:
        df: pandas.DataFrame
    """
    model = SeaweedModel()
    model.add_data_by_grid(path + os.sep + file)
    model.calculate_factors()
    model.calculate_growth_rate()
    model.create_section_dfs()
    param_df = model.construct_df_for_parameter(parameter)
    return param_df


def time_series_analysis(growth_df, n_clusters, global_or_country):
    """
    Does time series analysis on the dataframe
    All the time serieses are clustered based on their
    overall shape using k-means
    Inspired by this article:
    https://www.kaggle.com/code/izzettunc/introduction-to-time-series-clustering/notebook
    Arguments:
        growth_df: pandas.DataFrame
        n_clusters: int - the number of clusters to use
    Returns:
        labels: list - the labels for each time series
        km: TimeSeriesKMeans - the k-means object
    """
    # Make sure that each entry has a value
    assert growth_df.notna().all().all(), "The dataframe has nan"
    # Normalize the data
    scaler = MinMaxScaler()
    growth_df_scaled = pd.DataFrame(
        scaler.fit_transform(growth_df), columns=growth_df.columns
    )
    # A good rule of thumb is choosing k as the square root of the number
    # of points in the training data set in kNN
    cores = -1  # define the cores to use
    km = TimeSeriesKMeans(n_clusters=n_clusters, metric="dtw", n_jobs=cores)
    timeseries_ds = to_time_series_dataset(growth_df_scaled)
    labels = km.fit_predict(timeseries_ds)
    return labels, km


def elbow_method(growth_df, max_clusters, global_or_country, scenario):
    """
    Finds the optimal number of clusters using the elbow method
    https://predictivehacks.com/k-means-elbow-method-code-for-python/
    Arguments:
        growth_df: pandas.DataFrame
        max_clusters: int - the maximum number of clusters to try
    Returns:
        None, just plots the elbow method and saves it
    """
    # Find the optimal number of clusters
    inertias = {}
    for i in range(2, max_clusters):
        print("Trying {} clusters".format(i))
        labels, km = time_series_analysis(growth_df, i, global_or_country)
        inertias[i] = km.inertia_
    inertias_df = pd.DataFrame.from_dict(inertias, orient="index")
    inertias_df.to_csv(
        "data"
        + os.sep
        + "interim_data"
        + os.sep
        + scenario
        + os.sep
        + "inertias_"
        + global_or_country
        + ".csv",
        sep=";",
    )
    ax = inertias_df.plot(legend=False, linewidth=2.5, color="black")
    ax = inertias_df.plot(legend=False, linewidth=2)
    ax.set_xlabel("Number of clusters")
    ax.set_ylabel("Distortion")
    ax.set_title("Elbow method")
    ax.get_figure().savefig(
        "results"
        + os.sep
        + "elbow_plots"
        + os.sep
        + "elbow_method_"
        + global_or_country
        + "_"
        + scenario
        + ".png"
    )


def lme(scenario):
    """
    Calculates growth rate and all the factors for the lme
    and saves it in files appropriate for the plotting functions
    Arguments:
        None
    Returns:
        None
    """
    print("Working on LME data")
    model = SeaweedModel()
    model.add_data_by_lme(
        [i for i in range(1, 67)],
        "data/lme_data/seaweed_environment_data_in_nuclear_war.csv",
    )
    model.calculate_factors()
    model.calculate_growth_rate()
    model.create_section_dfs()
    # Define the parameters we look at
    parameters = [
        "salinity_factor",
        "nutrient_factor",
        "illumination_factor",
        "temp_factor",
        "nitrate_subfactor",
        "ammonium_subfactor",
        "phosphate_subfactor",
        "seaweed_growth_rate",
    ]
    # only run this if the file does not exist
    if not os.path.isfile(
        "data" + os.sep + "interim_data" + os.sep + "seaweed_growth_rate_LME.pkl"
    ):
        print("Creating the dataframe")
        # Transpose the dataframe so that the time serieses are the columns
        # Get all the parameters
        for parameter in parameters:
            print("Getting parameter {}".format(parameter))
            growth_df = model.construct_df_for_parameter(parameter).transpose()
            growth_df.to_pickle(
                "data"
                + os.sep
                + "interim_data"
                + os.sep
                + scenario
                + os.sep
                + parameter
                + "_LME.pkl"
            )


def grid(scenario, global_or_country, with_elbow_method=False):
    """
    Calculates growth rate and all the factors for the grid
    and saves it in files appropriate for the plotting functions
    Arguments:
        None
    Returns:
        None
    """
    print("Working with the gridded data")
    # Define the parameters we look at
    parameters = [
        "salinity_factor",
        "nutrient_factor",
        "illumination_factor",
        "temp_factor",
        "nitrate_subfactor",
        "ammonium_subfactor",
        "phosphate_subfactor",
        "seaweed_growth_rate",
    ]
    # only run this if the file does not exist as creating it takes a long time
    if not os.path.isfile(
        "data"
        + os.sep
        + "interim_data"
        + os.sep
        + scenario
        + os.sep
        + "seaweed_growth_rate_"
        + global_or_country
        + ".pkl"
    ):
        print("Creating the dataframe")
        path = "data" + os.sep + "interim_data" + os.sep + scenario
        file = "data_gridded_all_parameters_" + global_or_country + ".pkl"
        # Get all the parameters
        for parameter in parameters:
            print("Getting parameter {}".format(parameter))
            # Transpose the dataframe so that the time serieses are the columns
            growth_df = get_parameter_dataframe(parameter, path, file).transpose()
            growth_df.to_pickle(
                "data"
                + os.sep
                + "interim_data"
                + os.sep
                + scenario
                + os.sep
                + parameter
                + "_"
                + global_or_country
                + ".pkl"
            )
    if with_elbow_method:
        # Do the time series analysis
        growth_df = pd.read_pickle(
            "data"
            + os.sep
            + "interim_data"
            + os.sep
            + scenario
            + os.sep
            + "seaweed_growth_rate_"
            + global_or_country
            + ".pkl"
        )
        elbow_method(growth_df, 7, global_or_country, scenario)
    # elbow method says 3 is the optimal number of clusters
    num_clusters = {"global": 3, "US": 4, "AUS": 2}
    number_of_clusters = num_clusters[global_or_country]
    # Check if the files already exist
    if not os.path.isfile(
        "data"
        + os.sep
        + "interim_data"
        + os.sep
        + scenario
        + os.sep
        + "seaweed_growth_rate_clustered_"
        + global_or_country
        + ".pkl"
    ):
        # Cluster the data
        print("Clustering the data")
        growth_df = pd.read_pickle(
            "data"
            + os.sep
            + "interim_data"
            + os.sep
            + scenario
            + os.sep
            + "seaweed_growth_rate_"
            + global_or_country
            + ".pkl"
        )
        # Cluster only the growth data, as the other parameters all have the same shape
        labels, km = time_series_analysis(growth_df, number_of_clusters, global_or_country)
        growth_df["cluster"] = labels
        for parameter in parameters:
            print("Getting parameter {} for clustering".format(parameter))
            param_df = pd.read_pickle(
                "data"
                + os.sep
                + "interim_data"
                + os.sep
                + scenario
                + os.sep
                + parameter
                + "_"
                + global_or_country
                + ".pkl"
            )
            # Add the cluster labels to the dataframe
            param_df["cluster"] = labels
            param_df.to_pickle(
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
    else:
        growth_df = pd.read_pickle(
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


if __name__ == "__main__":
    lme("150tg")
    grid("150tg", "US")
    # # Iterate over all scenarios
    for scenario in [str(i) + "tg" for i in [5, 16, 27, 37, 47, 150]]:
        print("Preparing scenario: " + scenario)
        grid(scenario, "global")
    # # also run the control scenario
    grid("control", "global")
