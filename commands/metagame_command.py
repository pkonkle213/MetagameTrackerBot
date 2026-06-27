from discord import Interaction, app_commands
from discord.ext import commands

from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from output_builder import BuildTableOutput
from services.command_error_service import Error
from services.date_functions import BuildDateRange
from services.metagame_services import (
  FormatLockedMetagame,
  GetWholeMetagame,
  RegionLockedMetagame,
  StoreMetagame,
)
from settings import DATAGUILDID
from tuple_conversions import GameEnum, MetagameResult


class MetagameCommand(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="metagame", description="Get the metagame for this format")
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id, i.channel_id))
  @app_commands.guild_only()
  async def ViewMetagame(
    self, interaction: Interaction, start_date: str = "", end_date: str = ""
  ):
    """
    Parameters
    ----------
    start_date: string
      The start date of the metagame (MM/DD/YYYY)
    end_date: string
      The end date of the metagame (MM/DD/YYYY)
    """
    await interaction.response.defer(thinking=False)
    objects = GetObjectsFromInteraction(interaction)

    if not objects.game or not objects.format:
      raise KnownError("This channel is not set up with a game or format to view a metagame.")

    date_start, date_end = BuildDateRange(start_date, end_date, objects.format)

    if not interaction.channel_id:
      raise KnownError('Try a channel that has an id')

    #TODO: Wait, should this be in the service??
    if objects.game.id == GameEnum.Magic.value and objects.format.is_limited:
      archetype = "COALESCE(ua.archetype_played, 'Unknown') AS archetype_played,"
    else:
      archetype = "COALESCE(INITCAP(ua.archetype_played), 'Unknown') AS archetype_played,"

    title:str = ''
    data:list[MetagameResult] = []
    if interaction.guild_id == DATAGUILDID:
      data = GetWholeMetagame(objects.game, objects.format, date_start, date_end, archetype)
      title = f"{objects.format.format_name.title()} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}"
    elif objects.store:
      data = StoreMetagame(
        objects.store,
        objects.game,
        objects.format,
        date_start,
        date_end,
        archetype,
      )
      title = f"{objects.format.format_name.title()} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}"
    elif objects.hub and objects.hub.region_id:
      data = RegionLockedMetagame(
        objects.hub,
        objects.game,
        objects.format,
        date_start,
        date_end,
        archetype,
      )
      title = f"{objects.format.format_name.title()} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}"
    elif objects.hub:
      data = FormatLockedMetagame(
        objects.hub,
        objects.game,
        objects.format,
        objects.region,
        date_start,
        date_end,
        archetype
      )
      title_name = objects.region.region_name.title() if objects.region else 'General ' + objects.format.format_name.title()
      title = f"{title_name} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}"
    else:
      raise KnownError(
        "This channel is not set up with a store or hub to view a metagame."
      )

    if len(data) == 0:
      await interaction.followup.send(
        "No metagame data found for this discord and format"
      )
    else:
      headers = ["Deck Archetype", "Meta %", "Win %"]
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output)

  @ViewMetagame.error
  async def Errors(
    self, interaction: Interaction, error: app_commands.AppCommandError
  ):
    await Error(self.bot, interaction, error)


async def setup(bot:commands.Bot):
  await bot.add_cog(MetagameCommand(bot))
