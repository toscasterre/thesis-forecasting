# for type stubs
from typing import Optional

import pandas as pd
import holidays

# plotting
import matplotlib.pyplot as plt
import plotly.express as px
import custom_functions.plot_styles as ps

# time series
import statsmodels.tsa.api as tsa
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# use this to print out colored output with `print()`


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


def milan_holidays(ts: pd.DataFrame) -> pd.Series:
    """Requires a DataFrame with a DateTimeIndex"""
    ita_holidays = holidays.CountryHoliday(
        "IT",
        prov="MI",
        years=[year for year in list(ts.index.year.unique())]
    )

    # you cannot use `.apply()` on Indexes, but you
    # can cast an Index as a Series!
    return pd.DataFrame(ts.index, index=ts.index).iloc[:, 0] \
        .apply(lambda x: ita_holidays.get(str(x)))\
        .fillna("None").astype("category")


def create_ts_features(
    dataframe: pd.DataFrame,
    features: list = ["day", "month"]
) -> pd.DataFrame:
    """
        Generates time-series features out of a dataframe.
        The index MUST be a DateTimeIndex.

        Args:
        dataframe ([type]):
            DateTimeIndex-ed Pandas DataFrame.

        features (list, optional):
            The number of features to extract.
            Defaults to ["day", "month", "year"].
            Possible values:
            ["hour", "day", "month", "is_weekend", "week",
            "year", "day_name", "month_name", "holidays"]

            One note: week numbers depend on the year.
            Sometimes the last days of one year may actually be part
            of the following years' first week, as it is the case with 2019.
            (this can help to spot the overlapping days:
            `dataframe.index.isocalendar().week.reset_index().groupby("week").size()`)

        Returns the same dataframe, but with new columns
    """
    # this can also work:
    # df['month'] = [d.strftime('%b') for d in df.Fu]

    if "hour" in features:
        dataframe["hour"] = dataframe.index.hour.astype("category")

    if "day" in features:
        dataframe["day"] = (dataframe.index.day.astype("int") + 1) \
            .astype("category")

    if "day_names" in features:
        dataframe["day_name"] = dataframe.index.day_name().astype("category")

    if "weekends" in features:
        dataframe["is_weekend"] = dataframe.index.isocalendar().day \
            .apply(lambda x: 1 if x in [6, 7] else 0).astype("category")

    if "week" in features:
        dataframe["week"] = dataframe.index.isocalendar() \
            .week.astype("category")

    if "month" in features:
        dataframe["month"] = dataframe.index.month.astype("category")

    if "month_name" in features:
        dataframe["month_name"] = dataframe.index.month_name() \
            .astype("category")

    if "year" in features:
        dataframe["year"] = dataframe.index.year.astype("category")

    if "holidays" in features:
        dataframe["holiday"] = milan_holidays(dataframe).astype("category")

    return dataframe


def rolling_statistics(
        ts: pd.Series,
        lags: int,
        statistics: list = ["mean"]) -> None:
    """Plots the rolling statistics of a time series."""

    fig, ax = plt.subplots()

    # colors via tableau palette (tab:<colname>)
    ax.plot(ts, color="tab:blue", label="Observed Values")  # actual series

    if "mean" in statistics:  # if specified, plot rolling mean
        ax.plot(ts.rolling(lags).mean(),
                color="tab:red",
                label="Rolling Mean")

    if "std" in statistics:  # if specified, plot rolling standard deviation
        ax.plot(ts.rolling(lags).std(),
                color="tab:gray",
                label="Rolling Standard Deviation")

    if "mean" in statistics:
        if "std" in statistics:
            title = "Rolling Mean and Standard Deviation"
        else:
            title = "Rolling Mean"
    else:
        title = "Rolling Standard Deviation"

    title += f"\nWindow size: {lags}"

    ax.set_title(title)
    ax.legend(loc="best")
    plt.show()


def get_time_format(time_unit: str) -> Optional[str]:
    """
    Takes a string such as "month" and returns
    the corresponding format for functions like `strftime`.

    Args:
    time_unit (string): a string with a time unit.
    Values accepted:
    ["year","month","weekday","hour","minute","second"]

    Returns:
    [string]: one of the following:
    ["%Y","%B","%A","%H","%M","%S"]
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


def default_boxplot_props(
        line_width: float = 1.5,
        median_linewidth: float = 2.5,
        whiskers_linewidth: int = 1,
        median_color: str = "tomato") -> dict:
    # colors: https://matplotlib.org/stable/gallery/color/named_colors.html
    return dict(
        boxprops=dict(lw=line_width),
        medianprops=dict(lw=median_linewidth),
        whiskerprops=dict(lw=whiskers_linewidth),
        capprops=dict(lw=line_width)
    )


def subunits_boxplot(
        ts: pd.Series,
        y: str,
        time_subunit: str,
        boxplot_props: dict = default_boxplot_props()) -> None:
    """
    Plots a time-series y againsts a subunit of its time column/index.
    Accepted time-subunits are: year, month, weekday, hour, minute, second.
    """
    # duplicate the inputted time series to prevent overwriting
    ts_ = pd.DataFrame(ts)

    # obtain the time format from the input subunit
    # e.g. "%B" and "month"
    time_format = get_time_format(time_subunit)

    # create the new subunit column for pivoting
    ts_[time_subunit] = ts_.index.strftime(time_format)

    # create a sorting key to reorder columns after pivoting
    sorting_key = list(ts_[time_subunit].unique())

    # pivot time series and reorder columns
    df = ts_.pivot(columns=time_subunit, values=y).reindex(columns=sorting_key)

    return ps.plotly_style(
        df.plot(
            kind="box",
            title=f"Bike Rentals {time_subunit.capitalize()} Boxplot",
            color_discrete_sequence=px.colors.qualitative.T10
        ))


def plot_acf_and_pacf(ts: pd.Series) -> None:
    """Plots pd.Series autocorrelation (ACF)
    and partial-autocorrelation function (PACF)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    plot_acf(ts, title="Autocorrelation (95% CI)", ax=ax1)
    plot_pacf(ts, title="Partial Autocorrelation (95% CI)", ax=ax2)
    plt.show()


def perform_adfuller(ts: pd.Series, regression: str = "ct") -> None:
    """
    Plots the rollign statistics of a time series,
    then performs the Advanced Dickey-Fuller test for stationarity.

    ADF Null Hypothesis is that there is a unit root,
    i.e. the series is non-stationary.
    To reject the null hypothesis (i.e., the series is stationary),
    the test statistics must be smaller than the critical value.

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
        {color.BOLD}The series is
        {f'{color.RED}non-' if adf_results[1] > 0.05 else ''} stationary
        {color.END}
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