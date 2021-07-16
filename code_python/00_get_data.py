# %% [markdown]
# # Import Libraries
# %%
from IPython import get_ipython

# custom functions
import custom_functions as funcs

# %% [markdown]
# # Retrieve Daily Datasets
#
# First, we run a custom script to check if the `PostgreSQL` server is started or to start it.

# %%
get_ipython().system('bash $MYBINS/pg_server_status')

# %% [markdown]
# As explained in the previous chapter, inserting the data into an SQL database enables faster operations on the data - which in this case amount in most instances to `GROUP BY`. Data is hence served much faster.
#
# Now, two datasets are retrieved: the daily outflow for the whole municipality of Milan and the daily outflow for each station in the city. The custom function `retrieve_bike_flow` has an argument, `time_column` which has a predefined value: `{"data_prelievo": "giorno_partenza"}`. This implies that the function will retrieve data aggregated on the time by which the bikes leave the station and not when they are returned once the ride is finished. In other words, by default the daily outflow will be retrieved. The parameter `trunc` is set to default to `day`: this will mean that the `time_column` will be truncated to the daily level - but this parameter can be set to other time units, such as `hour` to retrive hourly data.

# %%
# when no argument other than the table name is specified, daily data for Milan is retrieved
daily_outflow = funcs.retrieve_bike_flow(table="bikemi_2019")
daily_outflow.head()


# %%
# when the station_columns is specified, data for each station is retrieved
station_daily_outflow = (
    funcs.retrieve_bike_flow(
        table="bikemi_2019",
        station_column={"nome_stazione_prelievo": "stazione_partenza"}
    )
    .pipe(funcs.pivot_bike_flow, cols="stazione_partenza")
    .convert_dtypes()  # make double into integers
)

station_daily_outflow.head()

# %% [markdown]
# ## Filter out invalid data
#
# Before proceeding with the time series analysis, we first need to check out if the retrieved data belongs to the 2019. (Quick note: since the index is a datetime index, we can subset the data very easily by using, for example, this notation: `daily_outflow.loc["2019-10"]`.)
#
# The quickest way of doing it is by checking the length of our datasets:

# %%
print(
    f"Lenght of `daily_outflow` is {len(daily_outflow)}\nLength of `station_daily_outflow` is {len(station_daily_outflow)}")

# %% [markdown]
# We can further inspect the issue by looking at the last values of either dataset:

# %%
daily_outflow.tail()

# %% [markdown]
# How come 31 trips from the year 2020 sneaked in? The data comes from several `.xlsx` files that were put into a local database, to make retrieval faster. In other words, these observations were already there. If the analysis is performed by concatenating all tables for all years, the problem will be fixed. In the meantime, dropping these observations will do.

# %%
daily_outflow = daily_outflow.loc[daily_outflow.index != "2020-01"]
station_daily_outflow = station_daily_outflow.loc[station_daily_outflow.index != "2020-01"]

# %%

daily_outflow.to_csv("../data/bikemi_csv/daily_outflow.csv")
station_daily_outflow.to_csv("../data/bikemi_csv/station_daily_outflow.csv")
# %%
