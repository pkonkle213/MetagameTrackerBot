from data.map_claim_feed_data import AddClaimFeedMap
from interaction_data import GetInteractionData

def MapClaimFeed(interaction):
  game, format, store, userId = GetInteractionData(interaction, game=True, store=True)
  claim_map = AddClaimFeedMap(interaction.guild_id,
                              interaction.channel_id,
                              game.ID)
  if claim_map is None:
    raise Exception('Failed to map claim feed. Please try again later.')
  return f'Claim feed for {game.Name.title()} has been set to {interaction.channel.name}'