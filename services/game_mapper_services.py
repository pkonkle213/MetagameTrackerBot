from discord import Interaction, TextChannel, CategoryChannel
from custom_errors import KnownError
from data.games_data import AddGameMap, GetAllGames
from tuple_conversions import Game, Store


async def AddStoreGameMap(store: Store, category: CategoryChannel, chosen_game: Game):
    await AddGameMap(store.discord_id, chosen_game[0], category.id)
    return f"Success! This category ({category.name}) is now mapped to {chosen_game[1].title()}"


async def GetGameOptions():
    return await GetAllGames()
