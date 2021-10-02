import pandas as pd
import matplotlib.pyplot as plt

# time series
import statsmodels.tsa.api as tsa
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


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
