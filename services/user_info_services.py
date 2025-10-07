from discord import Interaction, Member
from custom_errors import KnownError
from data.get_user_info_data import GetLastArchetype, GetPlayerName, GetWinPercentage, GetMostPlayed
from interaction_objects import GetObjectsFromInteraction
from tuple_conversions import Format, Game, Store

def GetUserData(interaction: Interaction,
               member: Member):
  """Gets the player name, win percent, last played, and top decks for a user"""
  data = GetObjectsFromInteraction(interaction,
                                   game=True,
                                   format=True,
                                   store=True)

  player_name = GetUserName(data.Store.DiscordId,member.id)
  win_percent = GetWinPercent(member.id,
                              data.Store,
                              data.Game,
                              data.Format)
  last_played = GetLastPlayed(member.id,
                              data.Store,
                              data.Game,
                              data.Format)
  top_decks = GetTopDecks(member.id,
                          data.Store,
                          data.Game,
                          data.Format)
  return player_name, win_percent, last_played, top_decks

def GetUserName(guild_id: int,
                member_id: int):
  """Gets the player name for the user in this discord"""
  player_name = GetPlayerName(member_id,
                             guild_id)
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