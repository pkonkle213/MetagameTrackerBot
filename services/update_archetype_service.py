from tuple_conversions import Store, Game, Format
from data.update_archetypes_data import AddUpdatedArchetypes
from discord import Interaction

def UpdateArchetypes(
  store:Store,
  game:Game,
  format:Format,
  old_archetype:str,
  new_archetype:str,
  interaction:Interaction
) -> int:
  is_submitter = True
  submitter_name = interaction.user.display_name + ' via MassUpdate'
  submitter_id = interaction.user.id
  submitter_discord_id = interaction.guild.id
  submitter_discord_name = interaction.guild.name 
  
  count = AddUpdatedArchetypes(store, game, format, old_archetype, new_archetype, is_submitter, submitter_name, submitter_id, submitter_discord_id, submitter_discord_name) 
  return count