"""Project-owned renderer for league leaderboard race videos."""

from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _period_label(start, end, progress: float) -> str:
    if isinstance(start, (pd.Timestamp, datetime, np.datetime64)) and isinstance(
        end, (pd.Timestamp, datetime, np.datetime64)
    ):
        start_time = pd.Timestamp(start)
        end_time = pd.Timestamp(end)
        current_time = start_time + (end_time - start_time) * progress
        return current_time.strftime("%b %d, %Y")
    return str(start if progress < 0.5 else end)


def _make_frames(
    frame: pd.DataFrame, steps_per_period: int
) -> list[tuple[np.ndarray, str]]:
    values = frame.to_numpy(dtype=float)
    labels = frame.index.to_list()
    frames = [(values[0], str(labels[0]))]

    for period in range(len(frame) - 1):
        start_values = values[period]
        end_values = values[period + 1]
        for step in range(1, steps_per_period + 1):
            progress = step / steps_per_period
            current_values = start_values + (end_values - start_values) * progress
            label = _period_label(labels[period], labels[period + 1], progress)
            frames.append((current_values, label))
    return frames


def _rank_players(
    values: np.ndarray, categories: list[str], n_bars: int
) -> tuple[list[str], np.ndarray]:
    indices = np.argsort(-values, kind="stable")[:n_bars]
    return [categories[index] for index in indices], values[indices]


def create_league_chart_race(
    df: pd.DataFrame,
    filename: str | Path,
    *,
    n_bars: int = 8,
    steps_per_period: int = 10,
    period_length: int = 1500,
    title: str = "League Points Leaders",
    figsize: tuple[float, float] = (6, 4),
) -> str:
    """Render a ranked, interpolated leaderboard animation as an MP4."""
    if df.empty:
        raise ValueError("Cannot render a leaderboard race without data")
    if n_bars < 1 or steps_per_period < 1 or period_length < 1:
        raise ValueError("Bar count and animation timing must be positive")

    target = Path(filename)
    if target.suffix.lower() != ".mp4":
        raise ValueError("League leaderboard races must be saved as MP4 files")
    if not animation.writers.is_available("ffmpeg"):
        raise RuntimeError("FFmpeg is required to render league leaderboard videos")

    chart_data = df.apply(pd.to_numeric, errors="raise").fillna(0)
    if not np.isfinite(chart_data.to_numpy(dtype=float)).all():
        raise ValueError("Leaderboard values must all be finite numbers")

    frames = _make_frames(chart_data, steps_per_period)
    categories = list(chart_data.columns)
    colors = plt.get_cmap("tab20")
    color_by_category = {
        category: colors(index % colors.N)
        for index, category in enumerate(categories)
    }
    max_value = max(float(chart_data.to_numpy().max()), 1.0)
    fps = max(1, round(steps_per_period * 1000 / period_length))

    target.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=figsize)

    def draw(frame_index: int):
        values, period = frames[frame_index]
        names, ranked_values = _rank_players(values, categories, n_bars)
        positions = np.arange(len(names))

        ax.clear()
        ax.barh(
            positions,
            ranked_values,
            color=[color_by_category[name] for name in names],
            height=0.78,
        )
        ax.set_yticks(positions, labels=names)
        ax.invert_yaxis()
        ax.set_xlim(0, max_value * 1.22)
        ax.set_title(title, loc="left", fontsize=15, fontweight="bold", pad=14)
        ax.text(
            1,
            1.02,
            period,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="#555555",
        )
        ax.set_xlabel("Points")
        ax.xaxis.grid(True, color="#dddddd", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0, labelsize=9)
        ax.tick_params(axis="x", labelsize=8, colors="#666666")
        for position, value in zip(positions, ranked_values):
            ax.text(
                value + max_value * 0.015,
                position,
                f"{value:,.0f}",
                va="center",
                fontsize=8,
                color="#333333",
            )
        return ax.patches

    movie = animation.FuncAnimation(
        fig,
        draw,
        frames=len(frames),
        interval=period_length / steps_per_period,
        repeat=False,
    )
    try:
        movie.save(
            str(target),
            writer=animation.FFMpegWriter(fps=fps, bitrate=1800),
            dpi=144,
        )
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        plt.close(fig)

    return str(target)
