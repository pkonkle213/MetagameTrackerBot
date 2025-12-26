from data.map_claim_feed_data import AddClaimFeedMap
from interaction_objects import GetObjectsFromInteraction

def MapClaimFeed(interaction):
  store, game, format = GetObjectsFromInteraction(interaction)
  claim_map = AddClaimFeedMap(interaction.guild_id,
                              interaction.channel_id,
                              game.GameId)
  if claim_map is None:
    raise Exception('Failed to map claim feed. Please try again later.')
  return f'Claim feed for {game.GameName.title()} has been set to {interaction.channel.name}'