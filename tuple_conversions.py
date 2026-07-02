from typing import Any, NamedTuple
from datetime import date, datetime
from enum import Enum

class EventType(Enum):
  """An enum of the different types of events"""
  Weekly = 1
  Tournament = 2
  League = 3

class ReportedAs(Enum):
  """An enum of how events are reported"""
  Pairings = 1
  Standings = 2

class GameEnum(Enum):
  """An enum of games in the database"""
  Magic = 1
  Lorcana = 2
  OnePiece = 3
  StarWarsUnlimited = 4
  Riftbound = 5

class PlayerStanding(NamedTuple):
  points: int
  win_percent: float
  rank: int

class TopPlayers(NamedTuple):
  player_name: str
  points: int
  win_percent: float
  
class MetagameResult(NamedTuple):
  archetype_played: str
  metagame_percent: float
  win_percent: float

class League(NamedTuple):
  id: int
  name: str
  description: str
  start_date: date
  end_date: date
  top_cut: int
  discord_id: int
  game_id: int
  format_id: int
  created_by: int
  last_updated: date
  created_date: date
  updated_by: int

class ChannelFormatMapping(NamedTuple):
  discord_id: int
  channel_id: int
  format_id: int

class HubsChannels(NamedTuple):
  discord_id: int
  channel_id: int

class Archetype(NamedTuple):
  event_id: int
  player_name: str
  archetype: str
  submitter_id: int
  submitter_name: str

class Format(NamedTuple):
  id: int
  format_name: str
  last_ban_update: date | None
  is_limited: bool

class Game(NamedTuple):
  id: int
  game_name: str

class Store(NamedTuple):
  discord_id: int
  discord_name: str
  store_name: str
  owner_id: int
  owner_name: str
  store_address: str
  used_for_data: bool
  region_id: int
  is_paid: bool

class Hub(NamedTuple):
  discord_id: int
  discord_name: str
  hub_name: str
  owner_id: int
  owner_name: str
  region_id: int
  game_lock: int
  format_lock: int
  is_paid: bool

class Region(NamedTuple):
  id: int
  region_name: str

class Event(NamedTuple):
  id: int
  custom_event_id: int | None
  league_id: int | None
  discord_id: int
  event_date: date
  game_id: int
  format_id: int
  last_update: int
  event_type_id: int
  event_name: str
  reported_as: int
  created_by: int
  created_at: datetime  

class Pairing(NamedTuple):
  player1_name: str
  player1_game_wins: int
  player2_name: str
  player2_game_wins: int
  round_number: int #TODO: Very curious why I can't put this first as there's a "strip" error

class Standing(NamedTuple):
  player_name: str
  wins: int
  losses: int
  draws: int

class EventInput(NamedTuple):
  id: int
  custom_event_id: int | None
  event_date: date | None
  event_name: str
  event_type_id: int
  round_number: int
  PairingData: list[Pairing] | None
  StandingData: list[Standing] | None
  ArchetypeData: dict[str, str] | None
  Errors: list[str] | None
  StoreID: int
  GameID: int
  FormatID: int

class InteractionObjects(NamedTuple):
  store  : Store | None
  hub    : Hub | None
  region : Region | None
  game   : Game | None
  format : Format | None

class DataConverted(NamedTuple):
  pairings_data   : list[Pairing] | None
  standings_data  : list[Standing] | None
  errors          : list[str] | None
  round_number    : int | None
  event_date      : date | None
  archetypes      : dict[str, str] | None
  custom_event_id : int | None

class LeaderboardRace(NamedTuple):
  event_date: date
  player_name: str
  points: int

class UserData(NamedTuple):
  player_name: str
  win_percent: float
  last_played: str
  top_decks: list[tuple[str, str]]

class OutputToBuild(NamedTuple):
  title: str
  headers: list[str]
  data: list[Any]

class Card(NamedTuple):
  deck_id: int
  quantity: int
  card_name: str
  is_mainboard: bool

class Deck(NamedTuple):
  id: int
  archetype_played: str
  wins: int
  losses: int
  draws: int