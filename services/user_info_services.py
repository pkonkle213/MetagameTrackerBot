from data.player_name_data import GetUserName
from discord import Interaction, Member
from custom_errors import KnownError
from data.get_user_info_data import GetLastArchetype, GetPlayerName, GetWinPercentage, GetMostPlayed
from interaction_objects import GetObjectsFromInteraction
from tuple_conversions import Format, Game, Store

def GetUserData(interaction: Interaction,
               member: Member):
  """Gets the player name, win percent, last played, and top decks for a user"""
  objects = GetObjectsFromInteraction(interaction)
  if not objects.store or not objects.game or not objects.format:
    raise Exception('Unable to get store, game, or format')

  player_name = GetPlayerName(objects.store.discord_id,
                            member.id)
  win_percent = GetWinPercent(member.id,
                              objects.store,
                              objects.game,
                              objects.format)
  last_played = GetLastPlayed(member.id,
                              objects.store,
                              objects.game,
                              objects.format)
  top_decks = GetTopDecks(member.id,
                          objects.store,
                          objects.game,
                          objects.format)
  return player_name, win_percent, last_played, top_decks

def GetPlayerName(guild_id: int,
                member_id: int):
  """Gets the player name for the user in this discord"""
  player_name = GetUserName(member_id)
  if player_name is None:
    raise KnownError('This person has not claimed any data')
  return player_name.title()

def GetWinPercent(member_id: int,
                  store: Store,
                  game: Game,
                  format: Format):
  win_percent = GetWinPercentage(member_id,
                                 store,
                                 game,
                                 format)

  if win_percent is None:
    raise KnownError('This person has not played any games in this format')
  return win_percent

def GetLastPlayed(member_id: int,
                store: Store,
                game: Game,
                format: Format):
  last_played = GetLastArchetype(member_id,
                                 store,
                                 game,
                                 format)

  if last_played is None:
    raise KnownError('This person has not played any games in this format')  
  return last_played

def GetTopDecks(member_id: int,
                store: Store,
                game: Game,
                format: Format):
  most_played = GetMostPlayed(member_id,
                              store,
                              game,
                              format)
  if most_played is None:
    raise KnownError('This person has not played any games in this format')
  return most_played