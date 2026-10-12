from custom_errors import KnownError
from data.games_data import GetAllGames, AddGameMap
from services.game_mapper_services import AddStoreGameMap
from tuple_conversions import Game, Store
from discord import ui, SelectOption, Interaction


class MapGameModal(ui.Modal, title="Map Game"):
    is_submitted = False

    def __init__(self, store: Store, games: list[Game] | None = None):
        super().__init__()
        self.store = store

        self.games = games or []

        game_options = [
            SelectOption(label=game.game_name, value=str(game.id))
            for game in self.games
        ]

        self.select_game = ui.Label(
            text="Game",
            component=ui.Select(options=game_options, required=True, max_values=1),
        )
        self.add_item(self.select_game)

    @classmethod
    async def create(cls, store: Store):
        games = await GetAllGames()
        return cls(store, games)

    async def on_submit(self, interaction: Interaction) -> None:
        selected_game = GetGame(self.select_game.component.values[0], self.games)
        await interaction.response.defer(thinking=False)
        result = await AddStoreGameMap(interaction, selected_game)
        await interaction.followup.send(result, ephemeral=True)

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.followup.send(
            f"Oops! Something went wrong: {error}", ephemeral=True
        )
        self.is_submitted = False

    async def on_timeout(self) -> None:
        self.is_submitted = False


def GetGame(selection: str, games: list[Game]) -> Game:
    for game in games:
        if game.id == int(selection):
            return game
    raise KnownError("Game selected not found")
