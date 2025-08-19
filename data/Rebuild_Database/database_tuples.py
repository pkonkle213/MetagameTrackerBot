from collections import namedtuple
from typing import Any, Tuple

ArchetypeSubmission = namedtuple('ArchetypeSubmission', ['EventId',
                                                         'PlayerName',
                                                         'ArchetypePlayed',
                                                         'DateSubmitted',
                                                         'SubmitterId',
                                                         'SubmitterUsername',
                                                         'Reported'])

def ConvertToArchetypeSubmission(object:tuple[Any, Any, Any, Any, Any, Any, Any, Any]):
  return ArchetypeSubmission(int(object[1]),
                             object[2],
                             object[3],
                             object[4],
                             int(object[5]),
                             object[6],
                             object[7])

