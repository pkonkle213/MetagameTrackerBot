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
  EventID: int
  PlayerName: str
  Archetype: str
  SubmitterID: int
  SubmitterName: str

class Format(NamedTuple):
  FormatId: int
  FormatName: str
  LastBanUpdate: date
  IsLimited: bool

class Game(NamedTuple):
  GameId: int
  GameName: str

class Store(NamedTuple):
  DiscordId: int
  DiscordName: str
  StoreName: str
  OwnerId: int
  OwnerName: str
  Address: str
  UsedForData: bool
  IsPaid: bool
  State: str
  Region: int
  IsHub: bool

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