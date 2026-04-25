from data.map_claim_feed_data import AddClaimFeedMap
from interaction_objects import GetObjectsFromInteraction

def MapClaimFeed(interaction):
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game:
    raise Exception('Unable to map claim feed. Please try again later.')

  claim_map = AddClaimFeedMap(interaction.guild_id,
                              interaction.channel_id,
                              objects.game.id)
  if claim_map is None:
    raise Exception('Failed to map claim feed. Please try again later.')
  return f'Archetype submission feed for {objects.game.game_name.title()} has been set to this channel, {interaction.channel.name}'