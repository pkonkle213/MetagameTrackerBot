from datetime import date
from io import BytesIO
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from custom_errors import KnownError
from data.store_attendance_data import GetStoreAttendanceGraph
from services.date_functions import BuildDateRange
from tuple_conversions import InteractionObjects

WIDTH = 1100
HEIGHT = 680
COLORS = ["#1F74AD", "#E98E2E", "#61A9BD", "#9267C6", "#44986D", "#D8524F", "#DD83C9", "#8D6C5B"]
TREND_COLOR = "#666666"


def _Font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold
        else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _Series(
    rows: list[Any], game_configured: bool, format_configured: bool
) -> dict[str, list[tuple[date, int]]]:
    series: dict[str, list[tuple[date, int]]] = {}
    for event_date, _event_name, game_name, format_name, players in rows:
        if format_configured:
            name = format_name
        elif game_configured:
            name = format_name
        else:
            name = game_name
        series.setdefault(str(name), []).append((event_date, int(players)))
    return series


def BuildAttendanceGraphImage(
    rows: list[Any],
    title: str,
    game_configured: bool,
    format_configured: bool,
) -> bytes:
    if not rows:
        raise KnownError("No attendance data found for this store and date range.")

    series = _Series(rows, game_configured, format_configured)
    all_dates = [event_date for values in series.values() for event_date, _ in values]
    min_date, max_date = min(all_dates), max(all_dates)
    if min_date == max_date:
        min_x, max_x = min_date.toordinal() - 1, max_date.toordinal() + 1
    else:
        min_x, max_x = min_date.toordinal(), max_date.toordinal()
    max_players = max(players for values in series.values() for _, players in values)
    y_max = max(1, int(max_players * 1.2 + 0.999))

    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    title_font, label_font = _Font(27, True), _Font(15)
    draw.text((65, 24), title, fill="#222222", font=title_font)
    draw.text((65, 62), "Players per event", fill="#555555", font=label_font)

    left, right, top, bottom = 100, 1040, 110, 570
    x_span, y_span = right - left, bottom - top

    def point(event_date: date, attendance: int) -> tuple[int, int]:
        x = left + round((event_date.toordinal() - min_x) / (max_x - min_x) * x_span)
        y = bottom - round(attendance / y_max * y_span)
        return x, y

    for tick in range(6):
        value = round(y_max * tick / 5)
        y = bottom - round(y_span * tick / 5)
        draw.line((left, y, right, y), fill="#E5E7EB", width=1)
        draw.text((left - 42, y - 8), str(value), fill="#555555", font=label_font)
    draw.line((left, top, left, bottom), fill="#555555", width=2)
    draw.line((left, bottom, right, bottom), fill="#555555", width=2)

    for tick in range(5):
        ordinal = min_x + round((max_x - min_x) * tick / 4)
        date_value = date.fromordinal(ordinal)
        x = left + round(x_span * tick / 4)
        draw.line((x, bottom, x, bottom + 5), fill="#555555", width=1)
        draw.text((x - 35, bottom + 12), date_value.strftime("%m/%d/%y"), fill="#555555", font=label_font)

    for series_index, (name, values) in enumerate(sorted(series.items())):
        color = COLORS[series_index % len(COLORS)]
        values.sort(key=lambda value: value[0])
        coords = [point(event_date, attendance) for event_date, attendance in values]
        if len(coords) > 1:
            draw.line(coords, fill=color, width=3)
        for x, y in coords:
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color, outline="white", width=1)

        if format_configured:
            x_values = [event_date.toordinal() for event_date, _ in values]
            y_values = [attendance for _, attendance in values]
            mean_x = sum(x_values) / len(x_values)
            mean_y = sum(y_values) / len(y_values)
            denominator = sum((x - mean_x) ** 2 for x in x_values)
            slope = (
                sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values))
                / denominator
                if denominator
                else 0
            )
            intercept = mean_y - slope * mean_x
            trend_points = [
                point(date.fromordinal(min_x), max(0, round(slope * min_x + intercept))),
                point(date.fromordinal(max_x), max(0, round(slope * max_x + intercept))),
            ]
            for start, end in zip(trend_points, trend_points[1:]):
                dx, dy = end[0] - start[0], end[1] - start[1]
                distance = max(1, int((dx * dx + dy * dy) ** 0.5))
                for offset in range(0, distance, 12):
                    begin = offset / distance
                    finish = min(offset + 6, distance) / distance
                    draw.line(
                        (
                            round(start[0] + dx * begin),
                            round(start[1] + dy * begin),
                            round(start[0] + dx * finish),
                            round(start[1] + dy * finish),
                        ),
                        fill=TREND_COLOR,
                        width=2,
                    )
            draw.text((left + 10, top + 8), "Trend", fill=TREND_COLOR, font=label_font)

        if not format_configured:
            legend_x, legend_y = left + 15, top + 12 + series_index * 24
            draw.line((legend_x, legend_y + 8, legend_x + 22, legend_y + 8), fill=color, width=3)
            draw.text((legend_x + 30, legend_y), name, fill="#333333", font=label_font)

    draw.text((right - 75, bottom + 42), "Event date", fill="#555555", font=label_font)
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


async def GetAttendanceGraph(
    objects: InteractionObjects | None,
    start_date: str | None,
    end_date: str | None,
) -> bytes:
    if not objects or not objects.store:
        raise KnownError("This command must be run in a store server.")
    date_start, date_end = BuildDateRange(
        start_date or "", end_date or "", weeks=52
    )
    game_configured = objects.game is not None
    format_configured = game_configured and objects.format is not None
    rows = await GetStoreAttendanceGraph(
        objects.store,
        objects.game,
        objects.format if format_configured else None,
        date_start,
        date_end,
    )
    if format_configured:
        subject = objects.format.format_name.title()
    elif objects.game:
        subject = f"{objects.game.game_name.title()} by format"
    else:
        subject = "Attendance by game"
    title = f"{objects.store.store_name} attendance: {subject}"
    return BuildAttendanceGraphImage(
        rows, title, game_configured, format_configured
    )
