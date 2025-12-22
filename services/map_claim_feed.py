from data.map_claim_feed_data import AddClaimFeedMap
from interaction_objects import GetObjectsFromInteraction

def MapClaimFeed(interaction):
  game, format, store, userId = GetObjectsFromInteraction(interaction, game=True, store=True)
  claim_map = AddClaimFeedMap(interaction.guild_id,
                              interaction.channel_id,
                              game.GameId)
  if claim_map is None:
    raise Exception('Failed to map claim feed. Please try again later.')
  return f'Claim feed for {game.GameName.title()} has been set to {interaction.channel.name}'