from custom_errors import KnownError
from discord import ui, SelectOption, Interaction
from tuple_conversions import Hub, Region
from services.hub_region_service import AddHubRegionMap


class MapRegionModal(ui.Modal, title="Map Region"):
    def __init__(self, hub: Hub, regions: list[Region]):
        super().__init__()
        self.hub = hub
        self.regions = regions

        region_options = [
            SelectOption(label=region.region_name, value=str(region.id))
            for region in self.regions
        ]

        self.select_region = ui.Label(
            text="Region",
            component=ui.Select(options=region_options, required=True, max_values=1),
        )
        self.add_item(self.select_region)

    async def on_submit(self, interaction: Interaction) -> None:
        selected_region = GetRegion(
            self.select_region.component.values[0], self.regions
        )
        await interaction.response.defer(thinking=False)
        result = await AddHubRegionMap(self.hub, interaction, selected_region)
        await interaction.followup.send(result, ephemeral=True)


def GetRegion(selection: str, regions: list[Region]) -> Region:
    for region in regions:
        if region.id == int(selection):
            return region
    raise KnownError("Region selected not found")
