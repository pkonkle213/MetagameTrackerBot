from typing import NamedTuple
from datetime import date
from enum import Enum

#TODO: Implement these so that I'm not testing against "magic" strings
class EventType(Enum):
  Weekly = 1
  Tournament = 2

class ReportedAs(Enum):
  Pairings = 1
  Standings = 2

class GameEnum(Enum):
  Magic = 1
  Lorcana = 2
  StarWarsUnlimited = 3

class Archetype(NamedTuple):
  event_id: int
  player_name: str
  archetype: str
  submitter_id: int
  submitter_name: str

class Format(NamedTuple):
  format_id: int
  format_name: str
  last_ban_update: date
  is_limited: bool

class Game(NamedTuple):
  game_id: int
  game_name: str

class Store(NamedTuple):
  discord_id: int
  discord_name: str
  store_name: str
  owner_id: int
  owner_name: str
  address: str
  used_for_data: bool
  is_paid: bool
  state: str
  region: str
  is_hub: bool

class Event(NamedTuple):
  id: int
  custom_event_id: int | None
  discord_id: int
  event_date: date
  game_id: int
  format_id: int
  last_update: int
  event_type_id: int
  event_name: str
  reported_as: str

class Pairing(NamedTuple):
  P1Name: str
  P1Wins: int
  P2Name: str
  P2Wins: int
  Round: int

class Standing(NamedTuple):
  PlayerName: str
  Wins: int
  Losses: int
  Draws: int

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