import settings
from services.date_functions import BuildDateRange
from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction
from discord import app_commands, Interaction
from discord.ext import commands
from services.metagame_services import StoreMetagame, RegionLockedMetagame, FormatLockedMetagame, GetWholeMetagame
from output_builder import BuildTableOutput
from services.command_error_service import Error
from checks import IsStore

class MetagameCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="metagame",
                        description="Get the metagame for this format")
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  @app_commands.guild_only()
  async def ViewMetagame(self,
                   interaction: Interaction,
                   start_date: str = '',
                   end_date: str = ''):
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
      raise KnownError('This channel is not set up with a game or format to view a metagame.')

    date_start, date_end = BuildDateRange(start_date, end_date, objects.format)
    
    if objects.hub and objects.hub.format_lock:
      data = FormatLockedMetagame(
        objects.hub,
        interaction.channel_id,
        date_start,
        date_end
      )
    elif interaction.guild_id == settings.DATAGUILDID:
      data = GetWholeMetagame(
        objects.game,
        objects.format,
        date_start,
        date_end
      )
    elif objects.hub:
      data = RegionLockedMetagame(
        objects.hub,
        interaction.channel_id,
        date_start,
        date_end
      )
    elif objects.store:
      data = StoreMetagame(
        objects.store,
        objects.game,
        objects.format,
        date_start,
        date_end
      )
    else:
      raise KnownError('This channel is not set up with a store to view a metagame.')
      
    if data is None or len(data) == 0:
      await interaction.followup.send('No metagame data found for this store and format')
    else:
      title_name = objects.format.format_name.title() if format else game.game_name.title()
      title = f'{title_name} metagame from {date_start.strftime('%-m/%-d')} to {date_end.strftime('%-m/%-d')}'
      headers = ['Deck Archetype', 'Meta %', 'Win %']
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output)

  @ViewMetagame.error
  async def Errors(self,
                 interaction: Interaction,
                 error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(MetagameCommand(bot))
