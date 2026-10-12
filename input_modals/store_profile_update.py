from discord import ui, SelectOption, Interaction
from discord.ext import commands
from services.command_error_service import Error
from tuple_conversions import Store, Hub, Game, Format
from data.data_hubs_data import GetPossibleHubs


class StoreProfileModal(ui.Modal, title="Update Store Profile"):
    is_submitted = False

    def __init__(
        self,
        bot: commands.Bot,
        store: Store,
        game: Game | None,
        format: Format | None,
        possible_hubs: list[Hub] | None = None,
    ) -> None:
        super().__init__()
        self.bot = bot

        possible_hubs = possible_hubs or []
        self.select_hubs = [
            SelectOption(label=hub.hub_name, value=str(hub.discord_id))
            for hub in possible_hubs
        ]

        self.store_name = ui.Label(
            text="Store Name",
            component=ui.TextInput(
                placeholder="Store name",
                default=store.store_name if store else "",
                required=True,
            ),
        )
        self.add_item(self.store_name)

        self.store_address = ui.Label(
            text="Store Address",
            component=ui.TextInput(
                placeholder="Store address",
                default=store.store_address if store else "",
                required=False,
            ),
        )
        self.add_item(self.store_address)

        self.melee_id = ui.Label(
            text="Melee ClientId",
            component=ui.TextInput(placeholder="Melee ID", required=False),
        )
        self.add_item(self.melee_id)

        self.melee_secret = ui.Label(
            text="Melee Secret",
            component=ui.TextInput(placeholder="Melee Secret", required=False),
        )
        self.add_item(self.melee_secret)

        if len(self.select_hubs) > 0:
            self.approved_hubs = ui.Label(
                text="Approved Hubs",
                component=ui.Select(
                    placeholder="Select hubs",
                    options=self.select_hubs,
                    min_values=0,
                    max_values=len(self.select_hubs),
                    required=False,
                ),
            )
            self.add_item(self.approved_hubs)

    @classmethod
    async def create(cls, bot, store, game, format):
        possible_hubs = (
            await GetPossibleHubs(store, game, format) if store.region_id else []
        )
        return cls(bot, store, game, format, possible_hubs)

    async def on_submit(self, interaction: Interaction) -> None:
        self.submitted_hubs: list[int] = []
        if len(self.select_hubs) > 0:
            self.submitted_hubs = CreateHubList(self.approved_hubs.component.values)

        self.submitted_store_name = self.store_name.component.value
        self.submitted_store_address = self.store_address.component.value
        self.submitted_melee_id = (
            self.melee_id.component.value if self.melee_id.component.value else None
        )
        self.submitted_melee_secret = (
            self.melee_secret.component.value
            if self.melee_secret.component.value
            else None
        )
        self.is_submitted = True
        self.new_interaction = interaction
        await interaction.response.defer(thinking=True, ephemeral=True)

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await Error(self.bot, interaction, error)

    async def on_timeout(self) -> None:
        self.is_submitted = False


def CreateHubList(hub_ids: list[str]) -> list[int]:
    return [int(id) for id in hub_ids]
