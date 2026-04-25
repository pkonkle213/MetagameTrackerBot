from input_modals.submit_archetype_general_modal import SubmitArchetypeModal
from input_modals.submit_archetype_magic_limited_modal import MagicLimitedSubmitArchetypeModal
from input_modals.submit_archetype_lorcana_modal import LorcanaSubmitArchetypeModal
from tuple_conversions import Event, Game, Format, Store
from discord import Interaction
from discord.ext import commands

async def GetUserInput(
  bot: commands.Bot,
  userId:int,
  events:list[Event],
  interaction:Interaction,
  game:Game,
  format:Format,
  player_name:str,
  player_archetypes: list[str]
) -> None:
  '''Determines which modal to use based on the game and format'''
  if game.game_name.upper() == 'MAGIC' and format.is_limited:
    modal = MagicLimitedSubmitArchetypeModal(bot, game, format, userId, events, player_name, player_archetypes)
  elif game.game_name.upper() == 'LORCANA':
    modal = LorcanaSubmitArchetypeModal(bot, game, format, userId, events, player_name, player_archetypes)
  else:
    modal = SubmitArchetypeModal(bot, game, format, userId, events, player_name, player_archetypes)
  await interaction.response.send_modal(modal)
  await modal.wait()