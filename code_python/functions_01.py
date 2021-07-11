import psycopg2
import pandas as pd
import statsmodels.tsa.api as tsa
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
# from plotnine import *  # plots à la ggplot


class color:
    # define custom class to render formatted output
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def get_dict_items(dictio):
    """Auxiliary function to extract a tuple of key-value pairs from each dictionary item"""
    for key, value in dictio.items():
        return key, value


def retrieve_bike_flow(
    db_conn_detail={"dbname": "bikemi", "user": "luca"},
    table="_2019_q3",
    # e.g. station_column = {"nome_stazione_prelievo" : "stazione_partenza"}
    station_column=None,
    # alternatively, {"data_restituzione" : "giorno_restituzione"}
    time_column={"data_prelievo": "giorno_partenza"},
    trunc="day"
):
    """
    From the PostgreSQL database, extract a Pandas DataFrame containing the trips data grouped at a certain time interval.
    The time interval is any argument that can enter SQL `DATE_TRUNC()` syntax: it can be 'day', 'hour'...
    If `time_column` is `data_prelievo` then the function will return the outflow; if it is `data_restituzione` it will be the inflow.
    If `station_column` is specified, the data will be for each individual station.
    Data is already indexed at the `time_column`.
    """
    db_conn = psycopg2.connect(
        "dbname = {dbname} user = {user}".format(**db_conn_detail))

    time_key, time_val = get_dict_items(time_column)

    if station_column is None:

        query = f'''
            SELECT
                DATE_TRUNC('{trunc}', {time_key}) AS {time_val},
                COUNT(bici)
            FROM {table}
            GROUP BY {time_val};
            '''
    else:
        station_key, station_val = get_dict_items(station_column)

        query = f'''
            SELECT
                {station_key} AS {station_val},
                DATE_TRUNC('{trunc}', {time_key}) AS {time_val},
                COUNT(bici)
            FROM {table}
            GROUP BY {time_val}, {station_val};
            '''

    return pd.read_sql(query, con=db_conn, index_col=f"{time_val}")


def pivot_bike_flow(bike_flow, cols, vals="count"):
    """Transform the flow into a panel dataframe - i.e., the data in wide format - with a series for each station"""
    return bike_flow.pivot(columns=cols, values=vals)


def make_ts_plot(df, y="count"):
    df.plot(y=y, title=f"Daily {y.capitalize()} of Trips in Milan",
            xlabel="Time", ylabel=None)


def get_time_format(time_unit):
    """
    Takes a string such as "month" and returns the corresponding format for functions like `strftime`

    Args:
        time_unit (string): a string with a time unit.
        Values accepted are: ["year","month","weekday","hour","minute","second"]

    Returns:
        [string]: one of the following: ["%Y","%B","%A","%H","%M","%S"]
    """

    units_and_formats = {
        "year": "%Y",
        "month": "%B",
        "weekday": "%A",
        "hour": "%H",
        "minute": "%M",
        "second": "%S",
    }

    return units_and_formats.get(time_unit.lower())


def default_boxplot_props(line_width=1.5, median_linewidth=2.5, whiskers_linewidth=1, median_color="tomato"):
    # colors: https://matplotlib.org/stable/gallery/color/named_colors.html
    return dict(
        boxprops=dict(lw=line_width),
        medianprops=dict(lw=median_linewidth),
        whiskerprops=dict(lw=whiskers_linewidth),
        capprops=dict(lw=line_width)
    )


def subunits_boxplot(ts, y, time_subunit, boxplot_props=default_boxplot_props()):
    """
    Plots a time-series y againsts a subunit of its time column/index.
    Accepted time-subunits are: year, month, weekday, hour, minute, second.
    """
    # duplicate the inputted time series to prevent overwriting
    ts_ = ts.copy()

    # obtain the time format, e.g. "%B", from the subunit indicated, e.g. "month"
    time_format = get_time_format(time_subunit)

    # create the new subunit column for pivoting
    ts_[time_subunit] = ts_.index.strftime(time_format)

    # create a sorting key to reorder columns after pivoting
    sorting_key = list(ts_.index.strftime(time_format).unique())

    # pivot time series and reorder columns
    df = ts_.pivot(columns=time_subunit, values=y).reindex(columns=sorting_key)

    fig, ax = plt.subplots()
    df.plot(kind="box", ax=ax,
            title=f"Daily Outflow of Bikes, {time_subunit.capitalize()} Boxplots",
            **boxplot_props)


def plot_rolling_statistics(ts, lags=7):
    """Plots the rolling statistics of a time series."""
    # rolling statistics
    roll_mean = ts.rolling(lags).mean()
    roll_std = ts.rolling(lags).std()

    # plot rolling statistics
    fig, ax = plt.subplots()
    # colors via tableau palette (tab:<colname>)
    ax.plot(ts, color="tab:blue", label="Observed Values")
    ax.plot(roll_mean, color="tab:red", label="Rolling Mean")
    ax.plot(roll_std, color="tab:gray", label="Rolling Standard Deviation")
    ax.set_title("Rolling Mean and Standard Deviation")
    ax.legend(loc="best")
    plt.show()


def plot_acf_and_pacf(ts):
    """Takes a Pandas time series and outputs the autocorrelation and partial-autocorrelation function plots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    plot_acf(ts, title="Autocorrelation (95% CI)", ax=ax1)
    plot_pacf(ts, title="Partial Autocorrelation (95% CI)", ax=ax2)
    plt.show()


def perform_adfuller(ts, regression="ct"):
    """
    Plots the rollign statistics of a time series and then performs the Advanced Dickey-Fuller test for stationarity.

    ADF Null Hypothesis is that there is a unit root, i.e. the series is non-stationary.
    To reject the null hypothesis (i.e., the series is stationary), the test statistics must be smaller than the critical value

    Default test is with constant and trend.
    """

    # Advanced Dickey Fuller test:
    adf_results = tsa.adfuller(ts, regression=regression)

    results_string = f"""
        Test Statistics: {adf_results[0]}
        p-value: {adf_results[1]}\n
        Number of lags: {adf_results[2]}
        Number of observations: {adf_results[3]}\n
        Critical Value (1%): {adf_results[4].get("1%")}
        Critical Value (5%): {adf_results[4].get("5%")}
        Critical Value (10%): {adf_results[4].get("10%")}\n
        AIC: {adf_results[5]}\n
        {color.BOLD}The series is {f'{color.RED}non-' if adf_results[1] > 0.05 else ''}stationary {color.END}
        """
    print(results_string)

    # complicated version
    # for key, value in adf_results[4].items():
    #     if ad_res[0] > value:
    #         print(f"""
    #         We fail to reject the null hypothesis at the {key} level.
    #         The series appears to be non-stationary.
    #         """)
    #     else:
    #         print(f"""
    #         We reject the null hypothesis at the {key} level.
    #         The series appears to be stationary.
    #         """)


if __name__ == "main":
    pass
