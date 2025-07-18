from collections import namedtuple

InteractionDetails = namedtuple("InteractionDetails", ['Game',
                                                       'Format',
                                                       'DiscordId',
                                                       'ChannelId',
                                                       'UserId'])

Format = namedtuple('Format', ['ID',
                               'Name',
                               'LastBanUpdate'])

Game = namedtuple('Game', ['ID',
                           'Name',
                           'HasFormats'])

Store = namedtuple('Store', ['DiscordId',
                             'DiscordName',
                             'StoreName',
                             'OwnerId',
                             'OwnerName',
                             'ApprovalStatus',
                             'UsedForData',
                             'PaymentLevel'])

Participant = namedtuple('Participant',['PlayerName',
                                        'Wins',
                                        'Losses',
                                        'Draws'])

Event = namedtuple('Event', ['ID',
                             'StoreDiscordID',
                             'EventDate',
                             'GameID',
                             'FormatID',
                             'LastUpdate'])

Round = namedtuple('Round',['P1Name',
                            'P1Wins',
                            'P2Name',
                            'P2Wins',
                            'Round'])

def ConvertToRound(round_obj):
  return Round(round_obj[0],
               int(round_obj[1]),
               round_obj[2],
               int(round_obj[3]),
               int(round_obj[4]))

def ConvertToEvent(event_obj):
  return Event(int(event_obj[0]),
               int(event_obj[1]),
               event_obj[2],
               int(event_obj[3]),
               int(event_obj[4]) if event_obj[4] is not None else None,
               int(event_obj[5]))

def ConvertToStore(store):
  return Store(int(store[0]),
               store[1],
               store[2],
               int(store[3]),
               store[4],
               store[5],
               store[6],
               int(store[7]))

def ConvertToGame(game_obj):
  return Game(int(game_obj[0]),
              game_obj[1],
              game_obj[2])

def ConvertToFormat(format_obj):
  return Format(int(format_obj[0]),
                format_obj[1],
                format_obj[2])