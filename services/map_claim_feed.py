from discord import Interaction
from custom_errors import KnownError
from data.map_claim_feed_data import AddClaimFeedMap
from interaction_objects import GetObjectsFromInteraction

def MapClaimFeed(interaction:Interaction) -> str:
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game:
    raise Exception('Unable to map claim feed. Please try again later.')

  if not interaction.guild_id or not interaction.channel_id:
    raise KnownError("Cannot map something that doesn't have a guild or a channel")

  AddClaimFeedMap(interaction.guild_id,
                              interaction.channel_id,
                              objects.game.id)
  return f'Archetype submission feed for {objects.game.game_name.title()} has been set to this channel, {interaction.channel.name}'