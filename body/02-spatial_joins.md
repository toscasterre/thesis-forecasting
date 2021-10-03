---
jupytext:
  formats: notebooks///ipynb,body///md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.0
kernelspec:
  display_name: Deep Learning Forecasting
  language: python
  name: bikemi
---

+++ {"tags": []}

# Import Libraries and Load Data

```{code-cell} ipython3
# import custom functions for joins and cleaning strings
import custom_functions.clean_strings as cs
import custom_functions.joins as j

# main libs
import geopandas

# plotting
import matplotlib.pyplot as plt

# reading and manipulating data
import pandas as pd

# for nice output statements, such as with `print()`:
from rich.console import Console

%matplotlib inline

console = Console()
```

Let's import the data. `geopandas.GeoDataFrame` can have as many `geopandas.GeoSeries` objects within, but only one is active at a time.

```{code-cell} ipython3
# load stalls lon-lat table
bikemi_stalls = geopandas.read_file("../data/bikemi_metadata/bikemi_stalls.geojson")

# load NIL lon-lat table
nil = geopandas.read_file("../data/milan/milan_nil.geojson")

# actually not needed, municipi categorical var is already in bikemi_stalls
municipi = geopandas.read_file("../data/milan/milan_municipi.geojson")
```

```{code-cell} ipython3
# select only the column we need + rename
nil = (
    nil[["ID_NIL", "NIL", "geometry"]]
    .assign(NIL=lambda x: x["NIL"].str.title())
    .astype({"ID_NIL": "string", "NIL": "string"})
    .rename(columns={"NIL": "nil", "ID_NIL": "nil_number"})
    .set_index("nil_number")
    .sort_values("nil", ascending=True)
)

nil.info()
```

```{code-cell} ipython3
# select only the column we need + rename
bikemi_stalls = (
    bikemi_stalls[["nome", "zd_attuale", "geometry", "anno"]]
    .rename(columns={"zd_attuale": "municipio"})
    .sort_values(by=["nome"], ascending=True)
    .astype({"nome": "string", "municipio": "string"})
    .set_index("nome")
)

bikemi_stalls.info()
```

We have geometries. Let's make a first plot, to see how it looks like.

```{code-cell} ipython3
# define ax object and dimensions
fig, ax = plt.subplots(figsize=(10, 10))

# plot both objects on the same axes; order matters
nil.plot(ax=ax, cmap="Blues")
bikemi_stalls.plot(ax=ax, color="tab:red")

# remove the axis lines
plt.axis("off")
plt.show()
```

Finally, let's load the time series data:

```{code-cell} ipython3
# load the time series for each station in the long format
station_outflow = pd.read_csv(
    "../data/bikemi_csv/station_daily_outflow.csv",
    parse_dates=[0],
    index_col=[0],
    dtype={"stazione_partenza": "string"},
)

station_outflow.info()
```

+++ {"incorrectly_encoded_metadata": "tags=[] jp-MarkdownHeadingCollapsed=true"}

# First Join: BikeMi Stalls and Time Series Data

+++

## Tentative Join

```{code-cell} ipython3
# join the index of the table specified as the first argument on the column specified by the "on" argument
tentative_join = geopandas.GeoDataFrame(
    # the data to pass as first argument:
    station_outflow.join(bikemi_stalls, on="stazione_partenza").sort_values(
        ["giorno_partenza", "stazione_partenza"], ascending=True
    ),
    # then set the coordinate reference system
    crs="EPSG:4326",
).astype({"stazione_partenza": "string"})

tentative_join.info()
```

Some information is actually lost! There are some observations from the dataset which cannot be matched to the stalls list.

```{code-cell} ipython3
unique_stalls = pd.Series(bikemi_stalls.index.unique())
unique_stations = pd.Series(
    station_outflow["stazione_partenza"].sort_values(ascending=True).unique(),
    name="stazione_partenza",
)

# using rich
console.print(
    f"""
Number of stalls in the official data: {unique_stalls.size}.
Number of stalls in our time series: {unique_stations.size}.
"""
)
```

## String Matching

+++

13 stalls are missing, but we are likely to find more mismatches. To deal with this, we have to turn to snake_case all station names, then perform the join again. We will have to use regular expressions. As Jamie Zawinski said in 1997:

> Some people, when confronted with a problem, think: "I know, I'll use regular expressions". Now they have two problems.

Here we apply some custom functions, which can be found in the omonimous folder under this directory.

```{code-cell} ipython3
clean_stalls = cs.clean_series(unique_stalls)
clean_stations = cs.clean_series(unique_stations)

j.mismatches(clean_stalls, clean_stations, left_on="nome", right_on="stazione_partenza")
mismatched_stations, mismatched_stalls = j.mismatches(
    clean_stalls,
    clean_stations,
    left_on="nome",
    right_on="stazione_partenza",
    text=False,
)
```

```{code-cell} ipython3
list(mismatched_stalls), list(mismatched_stations)
```

Some stations do not appear because they were introduced in 2020 and 2021, i.e. `Brunelleschi - Giambellino`. Others, such as `Gioia - Vespucci`, do not have a value for `anno`.

```{code-cell} ipython3
# take some time to appreciate how clean df.query() is:
bikemi_stalls.query("anno >= 2020 or anno.isna()")
```

This is another reason for aggregating the data to the NIL level: stations may change across this time span, whereas NIL stay the same for 10 years at least.

Now we can retry the join, after applying the custom function for cleaning strings to each column we plan to join.

+++

## Cleaned Data

```{code-cell} ipython3
clean_outflow = cs.clean_df(station_outflow, col="stazione_partenza", inplace=True)
clean_bikemi_stalls = cs.clean_df(
    bikemi_stalls.drop("anno", axis=1).reset_index(), col="nome", inplace=True
).set_index("nome")
```

```{code-cell} ipython3
geo_outflow = geopandas.GeoDataFrame(
    clean_outflow.join(clean_bikemi_stalls, on="stazione_partenza").iloc[::-1],
    crs="EPSG:4326",
).astype({"stazione_partenza": "string"})

geo_outflow.info()
```

Notice that we lose just a small part of the observations. Now it's finally time to perform the spatial joins to obtain the NIL from this data:

+++ {"tags": []}

# Two Spatial Joins

+++

Let's proceed with a spatial operation, to assign each stall to its NIL, i.e. neighbourhood. The spatial operations can be:

* `intersects`: if the object on the left is inside or on the boundary of the object on the right.
* `contains`: if the object on the left contains the one on the right (i.e. no part of right is outside of left).
* `within`: the opposite of `contains`.
* `touches`: if boundaries touch in at least one point, but none in the interior.
* `crosses`: more than one but not all points in common.
* `overlaps`: same as above, but the objects have the same dimension and yet do not coincide (see it as equivalence vs congruence).

+++ {"tags": []}

## Second Spatial Join: Georeferenced Time Series and Local Neighbourhoods (NIL)

```{code-cell} ipython3
geo_outflow_nil = (
    geopandas.sjoin(geo_outflow, nil, how="inner", op="intersects")
    .rename(
        columns={
            "geometry": "nil_geometry",
            "index_right": "nil_number",
            "nil": "nil_name",
        }
    )
    .set_geometry("nil_geometry")
    .astype(
        {
            "stazione_partenza": "string",
            "municipio": "string",
            "nil_number": "string",
            "nil_name": "string",
        }
    )
)

geo_outflow_nil.info()
```

```{code-cell} ipython3
geo_outflow_nil.head()
```

Let's see how many NILs actually end up in the data:

```{code-cell} ipython3
:tags: []

pd.DataFrame(geo_outflow_nil.nil_name.unique())
```

Basically, there are bikemi stations in only half of the NILs in Milan. ~~However, this operations disregards the null values by default. For example, let's `groupby()` NIL and count the number of rows, and see what the last values of this new `DataFrame` look like:~~ This will only occur if the `dtype` of `stazione_partenza` is `category`.

```{code-cell} ipython3
geo_outflow_nil.groupby("nil_name")["stazione_partenza"].count().sort_values(
    ascending=False
).reset_index()
```

From this view, we see that some NILs report less than 365 observations, i.e. the nieghbourhood likely includes only one station with many zeroes. These are indeed the neighbourhoods at the outer skirts of Milan and display a small number of observations because there is a small number of stations and other means of transportations are much more used.

To obtain a better view, we want to build a table with NILs and the number of stations inside each one. There are two ways of going about this:

1. Perform a spatial join from the NIL table and the Station Table.
2. Perform some convoluted operations on our data.

The end goal of this would be to come up with a list of all neighbourhoods where the number of stations is adequate for our analysis (say, greater than 5).

Each approach has its pros and cons. The first requires going back on our code and might be more straight forward, whereas the second is more direct but requires a `groupby` followed by an assignment with a double `lambda` function. As of now, we shall go with the second approach, which we discuss in the following paragraph.

+++

### `groubpy` and Double Lambda Function

+++

To obtain this table, we need to `groupby()` the data by `nil_name` and apply the `unique()` method to list all unique `stazione_partenza` in each NIL. This is necessary because if we were to simply apply `count()` or `size()` we would get the number of rows for each neighbourhoord. This on itself would be enough to give us a feel of how many stations there are in each NIL, but will not be straight-forward to use to decide which neighbourhoods to keep in.

```python
pd.DataFrame(geo_outflow_nil.reset_index().groupby("nil_name")["stazione_partenza"].unique())
```

The resulting `DataFrame` has a two columns: the name of the neighbourhood, plus a list of the stations inside it. We need to craft a lambda to count the number of stations and then assign these values to a new column for the table. This is why we cast the `groupby()` output as a `pd.DataFrame` - otherwise we would not be able to use the method `.assign()`. Unfortunately, using this method entails using a double `lambda`. The first `lambda` is needed to perform the assignment: `[...].assign(count = lambda x: x["stazione_partenza"]`. The second one is used inside the `apply()` method to retrieve the length of the list on each row.

This double `lambda` can be avoided by using a more primitive approach, i.e. by defining a variable to store the `groupby()` - say, `df` - and then creating a new column for this `df` in the following way:

```python
df["count"] = df["stazione_partenza"].apply(lambda x: len(x))
```

I am not a fan of this way of writing `pandas` code. It needlessly creates useless variables and makes the code more difficult to come back to. Instead, using `assign` is more readable and can be used at any point during transformations, thanks to method chaining. This is more esthetically pleasing and reminds me of the `tidyverse`, whose influence cannot be overstated. After all, even `pandas` provides methods to enforce a sort of `{dplyr}` syntax: `query()`, `assign()` and `flter()` are equivalents of `dplyr::filter()`, `dplyr::mutate()` and `dplyr::select()`.

Putting the two together, we get the following line of code:

```{code-cell} ipython3
nils_and_stations = (
    pd.DataFrame(
        geo_outflow_nil.reset_index().groupby("nil_name")["stazione_partenza"].unique()
    )
    .reset_index()
    .assign(count=lambda x: x["stazione_partenza"].apply(lambda x: len(x)))
    .sort_values("count")
)

nils_and_stations
```

To obtain a better view of this table, we can plot it:

```{code-cell} ipython3
# setting up plotly:
import plotly.express as px

pd.options.plotting.backend = "plotly"

nils_and_stations.plot(
    x="count",
    y="nil_name",
    kind="barh",
    title="Number of Stations per NIL",
    labels=dict(count="", nil_name=""),
    color_discrete_sequence=px.colors.qualitative.Vivid,
).update_layout({"template": "plotly_white", "font_family": "DejaVuSansMono Nerd Font"})
```

We could decide to take out all NILs with less than, say, 4 stations (included), but this would feel a bit arbitrary. Let us plot the correlation matrix, to get a better picture. First, we need to aggregate the data:

```{code-cell} ipython3
nil_daily_rentals = (
    geo_outflow_nil.reset_index()
    .groupby(["nil_name", "giorno_partenza"], as_index=False)["count"]
    .sum()
    .sort_values(by=["giorno_partenza", "nil_name"])
    .set_index("giorno_partenza")
    .pivot(columns="nil_name", values="count")
    .fillna(0)
    .astype("int64")
)

nil_daily_rentals
```

Then, we compute the correlation matrix.

```{code-cell} ipython3
import seaborn as sns

pd.options.plotting.backend = "matplotlib"
%matplotlib inline

# to use pandas dtypes in matplotlib plots
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

fig, ax = plt.subplots(figsize=(10, 10))

sns.heatmap(
    nil_daily_rentals.corr(),
    ax=ax,
    square=True,
    cmap=sns.diverging_palette(20, 230, as_cmap=True),
    linewidths=0.5,
    cbar_kws={"shrink": 0.5},
).set(xlabel="", ylabel="", title="Correlation Between Each Neighbourhood Time Series");
```

Such a plot is already elegant, but we might want to explot some interactive plotting libraries to better explore the values:

```{code-cell} ipython3
px.imshow(
    nil_daily_rentals.corr(),
    width=1000,
    height=1000,
    color_continuous_scale=px.colors.diverging.Geyser[::-1],
    labels={"x": "", "y": ""},
).update_layout(title_text="Correlation Across Neighbourhoods", font_family="Consolas")
```

These plots show that there are some stations that are totally uncorrelated with most of the others. We can obtain other insight from looking again at the geographical distribution of the data:

```{code-cell} ipython3
nil.head()
```

```{code-cell} ipython3
px.choropleth(
    nil,
    geojson=nil.geometry,
    locations=nil.nil,
    hover_name="nil",
    color_continuous_scale=px.colors.sequential.Plasma,
).update_layout(
    mapbox_style="open-street-map", height=500, margin={"r": 0, "t": 0, "l": 0, "b": 0}
)
```

```{code-cell} ipython3
px.choropleth_mapbox(
    nil,
    geojson=nil.geometry,
    locations=nil.index,
    hover_name="nil",
    color_continuous_scale=px.colors.sequential.Plasma,
).update_layout(
    mapbox_style="open-street-map", height=500, margin={"r": 0, "t": 0, "l": 0, "b": 0}
).update_geos(
    projection=dict(type="eckert4")
)
```

```{code-cell} ipython3
# good luck with the settings:
# https://plotly.com/python/reference/layout/geo/

px.scatter_mapbox(
    bikemi_stalls,
    lon=bikemi_stalls.geometry.x,
    lat=bikemi_stalls.geometry.y,
    hover_name=bikemi_stalls.reset_index()["nome"],
).update_layout(
    mapbox_style="open-street-map", height=500, margin={"r": 0, "t": 0, "l": 0, "b": 0}
).update_geos(
    projection=dict(type="eckert4")
)
```

# Save the Final Dataset

```{code-cell} ipython3
nil_aggregated_outflow.to_csv("../data/bikemi_csv/nil_daily_outflow.csv")
```

+++ {"tags": []}

# Appendix: Join with Municipi Data

+++

Finally, we might want to have preserved the `municipio` information:

```{code-cell} ipython3
nil_municipi = geopandas.sjoin(nil, municipi, how="inner", op="intersects")
```

```{code-cell} ipython3
nil_municipi.head()
```

```{code-cell} ipython3
:tags: []

nil_municipi = (
    nil_municipi[["nil", "MUNICIPIO", "geometry"]]
    .rename(
        columns={
            "nil": "nil_name",
            "MUNICIPIO": "municipio",
            "geometry": "geometry_municipio",
        }
    )
    .join(nil)
    .reset_index()
    .rename(columns={"geometry": "geometry_nil"})
    .drop("nil", axis=1)
)
```

The shape of the dataframe tells us that some `NIL` actually end un in multiple `Municipi`: for example, Brera spans across three!
