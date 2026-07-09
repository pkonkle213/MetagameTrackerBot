from discord import Interaction
from output_builder import BuildTableOutput
from data.invites_data import GetAllHubInvites
from interaction_objects import GetObjectsFromInteraction
from custom_errors import KnownError

def GetAllHubs(interaction:Interaction) -> str:
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.format:
    raise KnownError('No store or format found')

  hubs = GetAllHubInvites(objects.store, objects.format)
  print('Hubs:', hubs)
  title = 'Hubs Connected To This Store'
  headers = ['Hub Name', 'Invite URL']
  data = hubs
  output = BuildTableOutput(title, headers, data)
  return output