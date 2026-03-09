from data.map_claim_feed_data import AddClaimFeedMap
from interaction_objects import GetObjectsFromInteraction

def MapClaimFeed(interaction):
  store, game, format = GetObjectsFromInteraction(interaction)
  if not store or not game:
    raise Exception('Unable to map claim feed. Please try again later.')

  claim_map = AddClaimFeedMap(interaction.guild_id,
                              interaction.channel_id,
                              game.game_id)
  if claim_map is None:
    raise Exception('Failed to map claim feed. Please try again later.')
  return f'Archetype submission feed for {game.game_name.title()} has been set to this channel, {interaction.channel.name}'