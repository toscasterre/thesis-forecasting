# %% [markdown]
# # Time Series Analysis
#
# ## Import Libraries

# %%
import matplotlib as mpl
# import custom functions
import custom_functions as funcs

# set plots params
import matplotlib.pyplot as plt
plt.style.use("fivethirtyeight")  # change plot appearances

# customisations as ref, see:
# https://matplotlib.org/stable/tutorials/introductory/customizing.html
# https://matplotlib.org/stable/api/matplotlib_configuration_api.html#matplotlib.rcParams
mpl.rcParams["figure.figsize"] = (12, 6)  # set a figsize greater than default
mpl.rcParams["lines.linewidth"] = 2  # adjust line width
mpl.rc("font", family="monospace", monospace=["DejaVu Sans Mono"])
mpl.rc("axes", titlelocation="left", titlepad=12, titleweight="bold")


# ## Univariate Time Series Analysis
#
# Let's plot the data:

# %%
daily_outflow.plot(
    y="count",
    title="Daily Count of Trips in Milan",
    xlabel="Time",
    ylabel=None
)

# %% [markdown]
# The first thing that comes to mind is that the series displays a great variance. Then, there are three troughs, in correspondence of the major holidays: April with Easter, the weeks before and after August 15, and the end of the year. Clearly, the data is non-stationary. We can clearly see a trend, where the trip number increases until the middle of the year and then starts decreasing, reaching its lowest in the colder winter months. We can plot rolling means to get a better sense of these fluctuations.

# %%
for lag in [7, 30]:
    funcs.rolling_statistics(daily_outflow, lags=lag,
                             statistics=["mean", "std"])

# %% [markdown]
# We could plot the individual values for each month to display the difference in values. However, we can show these features better with a boxplot:

# %%
funcs.subunits_boxplot(daily_outflow, y="count", time_subunit="month")

# %% [markdown]
# However, the most important source of variation clearly is the weekly seasonality. The boxplot function is designed to accept various time formats, so we can adapt it pretty quickly:

# %%
funcs.subunits_boxplot(daily_outflow, y="count", time_subunit="weekday")

# %% [markdown]
# Given this distribution, we expect a strong relationship between data points that are seven lags from each other. More importantly, we expect that this variance will hinder the accuracy of our forecasts. This may require transforming the data (e.g. by taking logs or applying a Box-Cox transformation and searching for the optimal parameter $\lambda$) or *decomposing the time series*.
# %% [markdown]
# # Autocorrelation
#
# Let's have a look at the autocorrelation function, before proceeding.

# %%
funcs.plot_acf_and_pacf(daily_outflow["count"])

# %% [markdown]
# Both plots show that the data is (unsurprisingly) non stationary. Besides, the ACF plot shows two components of the time-series:
#
# * a trend, as the autocorrelation is declining;
# * a (strong) seasonal component on the seventh lag - i.e., a stron weekly dependence.
#
# The correlation quickly becomes statistically indistinguisheable from zero.
#
# Let's perform a Dickey Fuller test.
# %% [markdown]
# # Advanced Dickey Fuller Test

# %%
funcs.perform_adfuller(daily_outflow["count"])

# %% [markdown]
# The test statistic is greater than any critical value: in other words, we cannot reject the null hypothesis and the series is indeed non-stationary.
# %% [markdown]
# # Time-Series Decomposition
#
# There are several alternatives:
#
# * Apply a transformation (e.g., take logs);
# * Subtract the rolling average (it can work here, since the frequency is clear. It becomes more complex in case of high-frequency data: which window shall be selected?)

# %%
tsa.seasonal_decompose(daily_outflow, model="additive").plot()
