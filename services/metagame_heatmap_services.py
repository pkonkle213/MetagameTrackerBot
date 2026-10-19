from collections import OrderedDict
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from discord import File, Interaction

from data.metagame_heatmap_data import MetagameHeatmapRow

MAX_HEATMAP_DECKS = 16
CELL_WIDTH = 88
CELL_HEIGHT = 64
LEFT_MARGIN = 360
GRID_TOP = 470
OVERALL_WIDTH = 128
GRID_LEFT = LEFT_MARGIN + OVERALL_WIDTH + 20
OPPONENT_HEADER_Y = 128
COLUMN_LABEL_TOP = 154
OVERALL_HEADER_Y = GRID_TOP - 30
BACKGROUND = "#FFFFFF"
TEXT_COLOR = "#202124"
MUTED_COLOR = "#65717A"
GRID_COLOR = "#D3D9DD"


def SelectTopArchetypes(
    rows: list[MetagameHeatmapRow], limit: int = MAX_HEATMAP_DECKS
) -> tuple[list[str], dict[str, tuple[int, float | None]], dict[tuple[str, str], tuple[int, float | None]]]:
    deck_stats: OrderedDict[str, tuple[int, float | None]] = OrderedDict()
    matchups: dict[tuple[str, str], tuple[int, float | None]] = {}

    for row in rows:
        deck_stats.setdefault(
            row.archetype, (row.player_count, row.overall_win_percent)
        )
        if row.opponent_archetype is not None:
            matchups[(row.archetype, row.opponent_archetype)] = (
                row.games_against or 0,
                row.matchup_win_percent,
            )

    ranked = sorted(
        deck_stats,
        key=lambda name: (-deck_stats[name][0], name.casefold()),
    )[:limit]
    return ranked, dict(deck_stats), matchups


def BuildMetagameHeatmapImage(
    title: str, rows: list[MetagameHeatmapRow]
) -> bytes:
    archetypes, deck_stats, matchups = SelectTopArchetypes(rows)
    count = len(archetypes)
    grid_width = count * CELL_WIDTH
    image_width = GRID_LEFT + grid_width + 36
    image_height = GRID_TOP + count * CELL_HEIGHT + 44
    image = Image.new("RGB", (image_width, image_height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    title_font = _LoadFont(28, bold=True)
    header_font = _LoadFont(16, bold=True)
    body_font = _LoadFont(14)
    cell_font = _LoadFont(16, bold=True)
    small_font = _LoadFont(12)

    draw.text((32, 22), title, fill=TEXT_COLOR, font=title_font)
    draw.text(
        (32, 64),
        f"Top {count} archetypes by player count. Cell: matchup win rate / games played.",
        fill=MUTED_COLOR,
        font=body_font,
    )
    draw.text(
        (32, 91),
        "Red = lower win rate · green = higher win rate",
        fill=MUTED_COLOR,
        font=body_font,
    )

    draw.text(
        (GRID_LEFT, OPPONENT_HEADER_Y),
        "Opponent archetype",
        fill=TEXT_COLOR,
        font=header_font,
    )
    for index, archetype in enumerate(archetypes):
        x = GRID_LEFT + index * CELL_WIDTH
        _DrawVerticalText(
            image,
            archetype,
            _LoadFont(14, bold=True),
            TEXT_COLOR,
            x + CELL_WIDTH // 2,
            COLUMN_LABEL_TOP,
        )

    overall_x = LEFT_MARGIN
    draw.text(
        (overall_x + OVERALL_WIDTH // 2, OVERALL_HEADER_Y),
        "Overall",
        fill=TEXT_COLOR,
        font=header_font,
        anchor="mm",
    )

    for row_index, archetype in enumerate(archetypes):
        y = GRID_TOP + row_index * CELL_HEIGHT
        player_count = deck_stats[archetype][0]
        row_label = f"{archetype} ({player_count} players)"
        draw.text(
            (32, y + CELL_HEIGHT // 2),
            _FitText(draw, row_label, body_font, LEFT_MARGIN - 48),
            fill=TEXT_COLOR,
            font=body_font,
            anchor="lm",
        )

        overall_percent = deck_stats[archetype][1]
        overall_text = (
            f"{overall_percent:.1f}%" if overall_percent is not None else "N/A"
        )
        draw.rounded_rectangle(
            (
                overall_x,
                y + 3,
                overall_x + OVERALL_WIDTH - 4,
                y + CELL_HEIGHT - 3,
            ),
            radius=5,
            fill="#EEF1F3",
            outline=GRID_COLOR,
        )
        draw.text(
            (overall_x + (OVERALL_WIDTH - 4) // 2, y + CELL_HEIGHT // 2),
            overall_text,
            fill=TEXT_COLOR,
            font=cell_font,
            anchor="mm",
        )

        for column_index, opponent in enumerate(archetypes):
            x = GRID_LEFT + column_index * CELL_WIDTH
            rect = (x + 2, y + 2, x + CELL_WIDTH - 2, y + CELL_HEIGHT - 2)
            if opponent == archetype:
                fill = "#E6E9EB"
                draw.rounded_rectangle(
                    rect, radius=4, fill=fill, outline=GRID_COLOR
                )
                draw.text(
                    (x + CELL_WIDTH // 2, y + CELL_HEIGHT // 2),
                    "—",
                    fill=MUTED_COLOR,
                    font=cell_font,
                    anchor="mm",
                )
                continue

            matchup = matchups.get((archetype, opponent))
            if matchup is None or matchup[1] is None:
                fill = "#F4F5F6"
                percent_text = "N/A"
                games_text = "0 games"
            else:
                games, win_percent = matchup
                fill = _WinRateColor(win_percent)
                percent_text = f"{win_percent:.1f}%"
                games_text = f"{games} games"

            draw.rounded_rectangle(
                rect, radius=4, fill=fill, outline=GRID_COLOR
            )
            draw.text(
                (x + CELL_WIDTH // 2, y + 23),
                percent_text,
                fill=TEXT_COLOR,
                font=cell_font,
                anchor="mm",
            )
            draw.text(
                (x + CELL_WIDTH // 2, y + 44),
                games_text,
                fill=TEXT_COLOR,
                font=small_font,
                anchor="mm",
            )

    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def _LoadFont(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = (
        Path("/usr/share/fonts/truetype/dejavu") / filename,
        Path("/usr/share/fonts/dejavu") / filename,
    )
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def _DrawVerticalText(
    image: Image.Image,
    value: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    color: str,
    center_x: int,
    top_y: int,
) -> None:
    value = _FitText(
        ImageDraw.Draw(image),
        value,
        font,
        GRID_TOP - COLUMN_LABEL_TOP - 12,
    )
    bounds = font.getbbox(value)
    text_width = max(1, bounds[2] - bounds[0])
    text_height = max(1, bounds[3] - bounds[1])
    label = Image.new("RGBA", (text_width + 4, text_height + 4), (255, 255, 255, 0))
    label_draw = ImageDraw.Draw(label)
    label_draw.text(
        (2 - bounds[0], 2 - bounds[1]), value, font=font, fill=color
    )
    label = label.rotate(90, expand=True)
    image.paste(label, (center_x - label.width // 2, top_y), label)


def _FitText(
    draw: ImageDraw.ImageDraw,
    value: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> str:
    if draw.textlength(value, font=font) <= max_width:
        return value
    return _Ellipsize(draw, value, font, max_width)


def _Ellipsize(
    draw: ImageDraw.ImageDraw,
    value: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> str:
    suffix = "…"
    while value and draw.textlength(value + suffix, font=font) > max_width:
        value = value[:-1]
    return value + suffix if value else suffix


def _WinRateColor(win_percent: float) -> str:
    win_percent = float(win_percent)
    if win_percent == 50:
        return "#FFFFFF"

    tint = (220, 53, 69) if win_percent < 50 else (40, 167, 69)
    opacity = 0.12 + 0.48 * min(abs(win_percent - 50) / 50, 1.0)
    color = tuple(round(255 * (1 - opacity) + channel * opacity) for channel in tint)
    return "#{:02X}{:02X}{:02X}".format(*color)


async def SendMetagameHeatmap(
    interaction: Interaction, title: str, rows: list[MetagameHeatmapRow]
) -> None:
    image_bytes = BuildMetagameHeatmapImage(title, rows)
    await interaction.followup.send(
        file=File(BytesIO(image_bytes), filename="metagame_heatmap.png"),
        ephemeral=True,
    )
