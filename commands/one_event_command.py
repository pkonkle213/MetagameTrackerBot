from interaction_objects import GetObjectsFromInteraction
from custom_errors import KnownError
from discord import app_commands, Interaction
from discord.ext import commands
from input_modals.event_selector import EventSelector
from services.command_error_service import Error
from services.claim_result_services import OneEventDetails, OneEventMeta
from output_builder import BuildTableOutput

class OneEventCommands(commands.GroupCog, name='oneevent'):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='metagame',
    description='View the metagame for one event')
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def OneEventMeta(self, interaction:Interaction):
    store, game, format = GetObjectsFromInteraction(interaction)
    if not store or not game or not format:
      raise KnownError('No store, game, or format found.')

    modal = EventSelector(store, game, format)
    await interaction.response.send_modal(modal)
    await modal.wait()

    if not modal.is_submitted:
      raise Exception('Modal was not submitted')

    event = modal.event

    title, headers, data = OneEventMeta(event)
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)    
  
  @app_commands.command(name="topresults",
                       description="Get the archetypes for an event and their results")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def OneEvent(self,
                    interaction:Interaction):
    store, game, format = GetObjectsFromInteraction(interaction)
    if not store or not game or not format:
      raise KnownError('No store, game, or format found.')

    modal = EventSelector(store, game, format)
    await interaction.response.send_modal(modal)
    await modal.wait()

    if not modal.is_submitted:
      raise Exception('Modal was not submitted')

    event = modal.event

    title, headers, data = OneEventDetails(event)
    output = BuildTableOutput(title, headers, data)

    await interaction.followup.send(output)

  @OneEventMeta.error
  @OneEvent.error
  async def Errors(self,
                   interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(OneEventCommands(bot))