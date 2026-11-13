"""Pandas 3 compatibility for the unmaintained bar-chart-race 0.1.0 package."""

import pandas as pd

import bar_chart_race as bcr
from bar_chart_race import _make_chart


def prepare_wide_data(
    df,
    orientation="h",
    sort="desc",
    n_bars=None,
    interpolate_period=False,
    steps_per_period=10,
    compute_ranks=True,
):
    """Prepare wide data using current pandas forward-fill APIs."""
    if n_bars is None:
        n_bars = df.shape[1]

    df_values = df.reset_index()
    df_values.index = df_values.index * steps_per_period
    new_index = range(df_values.index[-1] + 1)
    df_values = df_values.reindex(new_index)

    if interpolate_period:
        if df_values.iloc[:, 0].dtype.kind == "M":
            first, last = df_values.iloc[[0, -1], 0]
            periods = pd.date_range(first, last, periods=len(df_values))
            df_values.iloc[:, 0] = periods
        else:
            df_values.iloc[:, 0] = df_values.iloc[:, 0].interpolate()
    else:
        df_values.iloc[:, 0] = df_values.iloc[:, 0].ffill()

    df_values = df_values.set_index(df_values.columns[0])
    if compute_ranks:
        df_ranks = df_values.rank(
            axis=1, method="first", ascending=False
        ).clip(upper=n_bars + 1)
        if (sort == "desc" and orientation == "h") or (
            sort == "asc" and orientation == "v"
        ):
            df_ranks = n_bars + 1 - df_ranks
        df_ranks = df_ranks.interpolate()

    df_values = df_values.interpolate()
    if compute_ranks:
        return df_values, df_ranks
    return df_values


def prepare_long_data(
    df,
    index,
    columns,
    values,
    aggfunc="sum",
    orientation="h",
    sort="desc",
    n_bars=None,
    interpolate_period=False,
    steps_per_period=10,
    compute_ranks=True,
):
    """Prepare long data using current pandas forward-fill APIs."""
    df_wide = df.pivot_table(
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc,
    ).ffill()
    return prepare_wide_data(
        df_wide,
        orientation,
        sort,
        n_bars,
        interpolate_period,
        steps_per_period,
        compute_ranks,
    )


# _BarChartRace.prepare_data looks up prepare_wide_data in this module's globals.
# Replace both public helpers and those internal references before charts are built.
_make_chart.prepare_wide_data = prepare_wide_data
_make_chart.prepare_long_data = prepare_long_data
bcr.prepare_wide_data = prepare_wide_data
bcr.prepare_long_data = prepare_long_data
