from collections import OrderedDict

from discord import Interaction

from data.metagame_heatmap_data import MetagameHeatmapRow


def BuildMetagameHeatmapMessages(
    title: str, rows: list[MetagameHeatmapRow]
) -> list[str]:
    archetypes: OrderedDict[str, dict[str, object]] = OrderedDict()
    matchups: dict[tuple[str, str], tuple[int, float]] = {}

    for row in rows:
        archetype = archetypes.setdefault(
            row.archetype,
            {
                "player_count": row.player_count,
                "overall_win_percent": row.overall_win_percent,
            },
        )
        if row.opponent_archetype is not None:
            matchups[(row.archetype, row.opponent_archetype)] = (
                row.games_against or 0,
                row.matchup_win_percent or 0.0,
            )

    ranked_archetypes = list(archetypes)
    lines = [
        f"**{title}**",
        "Matchup win-rate key: 🟦 under 45% · 🩵 45–49% · ⬜ 50–54% · 🟨 55–59% · 🟧 60%+",
        "",
    ]

    for rank, archetype_name in enumerate(ranked_archetypes, start=1):
        archetype = archetypes[archetype_name]
        overall_win_percent = archetype["overall_win_percent"]
        overall_text = (
            f"{overall_win_percent:.1f}%"
            if overall_win_percent is not None
            else "N/A"
        )
        lines.append(
            f"**{rank}. {archetype_name} — overall win rate: {overall_text}**"
        )

        for opponent_name in ranked_archetypes:
            if opponent_name == archetype_name:
                continue
            matchup = matchups.get((archetype_name, opponent_name))
            if matchup is None:
                lines.append(f"⬜ vs {opponent_name}: N/A (0 games)")
                continue

            games, win_percent = matchup
            lines.append(
                f"{_HeatColor(win_percent)} vs {opponent_name}: "
                f"{win_percent:.1f}% ({games} games)"
            )
        lines.append("")

    return _SplitDiscordMessages(lines)


def _HeatColor(win_percent: float) -> str:
    if win_percent < 45:
        return "🟦"
    if win_percent < 50:
        return "🩵"
    if win_percent < 55:
        return "⬜"
    if win_percent < 60:
        return "🟨"
    return "🟧"


def _SplitDiscordMessages(lines: list[str], max_chars: int = 1900) -> list[str]:
    messages: list[str] = []
    active_lines: list[str] = []
    active_length = 0

    for line in lines:
        if active_lines and active_length + len(line) + 1 > max_chars:
            messages.append("\n".join(active_lines))
            active_lines = []
            active_length = 0
        active_lines.append(line)
        active_length += len(line) + 1

    if active_lines:
        messages.append("\n".join(active_lines))
    return messages


async def SendMetagameHeatmap(
    interaction: Interaction, title: str, rows: list[MetagameHeatmapRow]
) -> None:
    for message in BuildMetagameHeatmapMessages(title, rows):
        await interaction.followup.send(message)
