#


### cluster_spatial
[source](https://github.com/allfed/Seaweed-Growth-Model/blob/master/src/plotting/plotter_grid.py/#L23)
```python
.cluster_spatial(
   growth_df, global_or_country, scenario, admin_1 = False
)
```

---
Creates a spatial plot of the clusters

**Arguments**

* **growth_df**  : a dataframe of the growth rate
* **global_or_country**  : a string of either "global" or "US" that indicates the scale


**Returns**

None, but saves the plot

----


### growth_rate_spatial_by_year
[source](https://github.com/allfed/Seaweed-Growth-Model/blob/master/src/plotting/plotter_grid.py/#L83)
```python
.growth_rate_spatial_by_year(
   growth_df, global_or_country, scenario, optimal_growth_rate
)
```

---
Plots the growth rate by year. This includes the first
three months without nuclear war, in the case of the first year

**Arguments**

* **growth_df**  : a dataframe of the growth rate


**Returns**

None, but saves the plot

----


### cluster_timeseries_all_parameters_q_lines
[source](https://github.com/allfed/Seaweed-Growth-Model/blob/master/src/plotting/plotter_grid.py/#L155)
```python
.cluster_timeseries_all_parameters_q_lines(
   parameters, global_or_country, scenario, areas
)
```

---
Plots line plots for all clusters and all parameters

**Arguments**

* **parameters**  : a dictionary of dataframes of all parameters


**Returns**

None, but saves the plot

----


### compare_nw_scenarios
[source](https://github.com/allfed/Seaweed-Growth-Model/blob/master/src/plotting/plotter_grid.py/#L294)
```python
.compare_nw_scenarios(
   areas, optimal_growth_rate
)
```

---
Compares the results of the nuclear war scenarios as weigthed median

**Arguments**

* **areas**  : A dataframe containing the area of each grid cell
* **eez**  : A eez around coastlines to only use those areas


**Returns**

None

----


### compare_nutrient_subfactors
[source](https://github.com/allfed/Seaweed-Growth-Model/blob/master/src/plotting/plotter_grid.py/#L415)
```python
.compare_nutrient_subfactors(
   nitrate, ammonium, phosphate, scenario, areas
)
```

---
Takes the weighted average of the nutrient subfactors globally and plots them
in the same plot to be able to compare them.

**Arguments**

* **nitrate**  : The nitrate subfactor
* **ammonium**  : The ammonium subfactor
* **phosphate**  : The phosphate subfactor
* **scenario**  : The scenario to plot
* **areas**  : The areas of the grid cells


**Returns**

None

----


### plot
[source](https://github.com/allfed/Seaweed-Growth-Model/blob/master/src/plotting/plotter_grid.py/#L483)
```python
.plot(
   scenario, global_or_country, optimal_growth_rate, admin_1 = False
)
```

---
Runs the other functions to read the data and make the plots

**Arguments**

* **scenario**  : The scenario to plot
* **global_or_country**  : Whether to plot the global or a country scenario
* **optimal_growth_rate**  : The maximum growth rate


**Returns**

None
