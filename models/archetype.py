from typing import NamedTuple

class Archetype(NamedTuple):
  """Represents a submitted archetype"""
  EventId: str
  PlayerName: str
  Archetype: str
  SubmitterId: str
  SubmitterName: str