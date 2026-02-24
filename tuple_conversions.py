from collections import namedtuple
from typing import Any, NamedTuple

from discord import datetime

Archetype = namedtuple('Archetype',
                       ['EventID',
                        'PlayerName',
                        'Archetype',
                        'SubmitterID',
                        'SubmitterName'])

def ConvertToArchetype(archetype_obj: tuple[Any, Any, Any, Any, Any]) -> Archetype:
  """Converts a tuple to an Archetype object."""
  return Archetype(int(archetype_obj[0]),
                   archetype_obj[1],
                   archetype_obj[2],
                   int(archetype_obj[3]),
                   archetype_obj[4])

Format = namedtuple('Format',
                    ['FormatId',
                     'FormatName',
                     'LastBanUpdate',
                     'IsLimited'])

def ConvertToFormat(format_obj: tuple[Any, Any, Any, Any]) -> Format:
  """Converts a tuple to a Format object."""
  return Format(int(format_obj[0]),
                format_obj[1],
                format_obj[2],
                format_obj[3])

Game = namedtuple('Game',
                  ['GameId',
                   'GameName'])

def ConvertToGame(game_obj: tuple[Any, Any]) -> Game:
  """Converts a tuple to a Game object."""
  return Game(int(game_obj[0]),
              game_obj[1])

Store = namedtuple('Store',
                   ['DiscordId',
                    'DiscordName',
                    'StoreName',
                    'OwnerId',
                    'OwnerName',
                    'Address',
                    'UsedForData',
                    'IsPaid',
                    'State',
                    'Region',
                    'IsHub'])

def ConvertToStore(store: tuple[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]) -> Store:
  """Converts a tuple to a Store object."""
  return Store(int(store[0]),
               store[1],
               store[2],
               int(store[3]),
               store[4],
               store[5],
               store[6],
               store[7],
               store[8],
               store[9],
               store[10])

class Event(NamedTuple):
  id: int
  custom_event_id: int | None
  discord_id: int
  event_date: datetime
  game_id: int
  format_id: int
  last_update: int
  event_type_id: int
  event_name: str
  reported_as: str
  
def ConvertToEvent(
  event_obj: tuple[int, int | None, str, int, int, int, str, str, str, bool, bool, int]
) -> Event:
  """Converts a tuple to an Event object."""
  try:
    return Event(int(event_obj[0]),
                 int(event_obj[1]) if event_obj[1] else None,
                 int(event_obj[2]),
                 event_obj[3],
                 int(event_obj[4]),
                 int(event_obj[5]),
                 event_obj[6],
                 event_obj[7],
                 event_obj[8],
                 event_obj[9])
  except Exception as e:
    raise Exception(f"Error converting event object: {e}")

class Pairing(NamedTuple):
  P1Name: str
  P1Wins: int
  P2Name: str
  P2Wins: int
  Round: int

Standing = namedtuple('Standing',
                      ['PlayerName',
                       'Wins',
                       'Losses',
                       'Draws'])

Data = namedtuple("Data",
                  ["Game",
                   "Format",
                   "Store",
                   "UserId"])

class EventInput(NamedTuple):
  ID: int
  CustomID: int | None
  Date: str
  Name: str
  TypeID: int
  RoundNumber: int
  PairingData: list[Pairing] | None
  StandingData: list[Standing] | None
  ArchetypeData: dict[str, str] | None
  Errors: list[str] | None
  StoreID: int
  GameID: int
  FormatID: int