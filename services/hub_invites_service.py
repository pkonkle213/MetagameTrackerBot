from discord import Interaction
from output_builder import BuildTableOutput
from data.invites_data import GetConnectedHubsInvites
from data.interaction_data import GetObjectsFromInteraction
from custom_errors import KnownError


async def GetConnectedHubs(interaction: Interaction) -> str:
    objects = await GetObjectsFromInteraction(interaction)
    if not objects.store or not objects.format:
        raise KnownError("No store or format found")

    hubs = await GetConnectedHubsInvites(objects.store, objects.format)
    title = "Hubs Connected To This Store"
    headers = ["Hub Name", "Invite URL"]
    data = hubs
    output = BuildTableOutput(title, headers, data)
    return output
