from discord import Interaction
from tuple_conversions import Hub, Region
from data.hubs_data import AddRegionMap

def AddHubRegionMap(hub:Hub, interaction:Interaction, region:Region) -> str:
  rows = AddRegionMap(hub, interaction.channel_id, region)
  return  f'Success! This channel ({interaction.channel.name}) is now mapped to the {region.region_name} region'