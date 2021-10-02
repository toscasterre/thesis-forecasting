from typing import Any, Tuple
import matplotlib as mpl
import matplotlib.pyplot as plt


def matplotlib_styles(
    figsize: Tuple[int, int] = (15, 6),
    linewidth: int = 2,
    font: str = "DejaVu Sans Mono"
) -> None:

    # custom theme
    plt.style.use("fivethirtyeight")  # change plot appearances

    # custom width
    # set a figsize greater than default
    mpl.rcParams["figure.figsize"] = figsize
    mpl.rcParams["lines.linewidth"] = linewidth  # adjust line width
    mpl.rc("font", family="monospace", monospace=[font])
    mpl.rc("axes", titlelocation="left", titlepad=12, titleweight="bold")


def plotly_style(
    fig: Any,
    font: str = "DejaVuSansMono Nerd Font"
) -> Any:
    """
    A shortcut to apply the settings I use most frequently for plotly figures.
    """
    return fig.update_layout(
        font_family=font,
        template="none",
        title={
            "x": 0.05,
            # basically, what part of the title to put at position "x"
            "xanchor": "left"
        }
    )
