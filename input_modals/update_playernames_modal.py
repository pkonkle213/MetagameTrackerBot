from custom_errors import KnownError
from tuple_conversions import Store, Game, Format
from discord import ui, Interaction
from data.update_player_names_data import (
    UpdatePlayerNamesInStandings,
    UpdatePlayerNamesInPairings,
    UpdatePlayerNameInArchetypes,
)
from services.input_services import ConvertInput


class UpdatePlayerNamesModal(ui.Modal, title="Update Player Names"):
    def __init__(self, store: Store, game: Game, format: Format):
        super().__init__()
        self.store: Store = store
        self.game: Game = game
        self.format: Format = format

        self.old_name = ui.Label(
            text="Old Name",
            component=ui.TextInput(placeholder="Old Name", required=True),
        )
        self.add_item(self.old_name)

        self.new_name = ui.Label(
            text="New Name",
            component=ui.TextInput(placeholder="New Name", required=True),
        )
        self.add_item(self.new_name)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        old_name = ConvertInput(self.old_name.component.value)
        new_name = ConvertInput(self.new_name.component.value)
        standings = UpdatePlayerNamesInStandings(
            self.store, self.game, self.format, old_name, new_name
        )

        pairings = UpdatePlayerNamesInPairings(
            self.store, self.game, self.format, old_name, new_name
        )

        if not standings and not pairings:
            raise KnownError(
                f"Unable to update player names: `{old_name}` to `{new_name}`"
            )

        archetypes = UpdatePlayerNameInArchetypes(
            self.store, self.game, self.format, old_name, new_name
        )
