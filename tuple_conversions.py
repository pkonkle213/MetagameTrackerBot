from collections import namedtuple
from typing import Any

Archetype = namedtuple('Archetype',
                       ['EventID',
                        'PlayerName',
                        'Archetype',
                        'SubmitterID',
                        'SubmitterName'])

def ConvertToArchetype(archetype_obj: tuple[Any, Any, Any, Any, Any]):
  """Converts a tuple to an Archetype object."""
  return Archetype(int(archetype_obj[0]),
                   archetype_obj[1],
                   archetype_obj[2],
                   int(archetype_obj[3]),
                   archetype_obj[4])

Format = namedtuple('Format',
                    ['ID',
                     'Name',
                     'LastBanUpdate',
                     'IsLimited'])

def ConvertToFormat(format_obj: tuple[Any, Any, Any, Any]):
  """Converts a tuple to a Format object."""
  return Format(int(format_obj[0]),
                format_obj[1],
                format_obj[2],
                format_obj[3])

Game = namedtuple('Game',
                  ['ID',
                   'Name',
                   'HasFormats'])

def ConvertToGame(game_obj: tuple[Any, Any, Any]):
  """Converts a tuple to a Game object."""
  return Game(int(game_obj[0]),
              game_obj[1],
              game_obj[2])

Store = namedtuple('Store',
                   ['DiscordId',
                    'DiscordName',
                    'StoreName',
                    'OwnerId',
                    'OwnerName',
                    'UsedForData',
                    'IsPaid'])

def ConvertToStore(store: tuple[Any, Any, Any, Any, Any, Any, Any]):
  """Converts a tuple to a Store object."""
  return Store(int(store[0]),
               store[1],
               store[2],
               int(store[3]),
               store[4],
               store[5],
               store[6])

Event = namedtuple('Event',
                   ['ID',
                    'StoreDiscordID',
                    'EventDate',
                    'GameID',
                    'FormatID',
                    'LastUpdate'])

def ConvertToEvent(event_obj: tuple[Any, Any, Any, Any, Any, Any]):
  """Converts a tuple to an Event object."""
  return Event(int(event_obj[0]),
               int(event_obj[1]),
               event_obj[2],
               int(event_obj[3]),
               int(event_obj[4]) if event_obj[4] else None,
               int(event_obj[5]))

Round = namedtuple('Round',
                   ['P1Name',
                    'P1Wins',
                    'P2Name',
                    'P2Wins',
                    'Round'])

Participant = namedtuple('Participant',
                         ['PlayerName',
                          'Wins',
                          'Losses',
                          'Draws'])
