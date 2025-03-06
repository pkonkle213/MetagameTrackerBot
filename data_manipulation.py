import date_functions
import database_connection
import output_builder
import settings
import tuple_conversions
from enum import Enum, auto

class Winner(Enum):
  TIE = auto()
  PLAYER1 = auto()
  PLAYER2 = auto()

def GetDataReport(discord_id, start_date, end_date):
  start = start_date if start_date != '' else '1/1/2024'
  date_start = date_functions.convert_to_date(start)
  date_end = date_functions.convert_to_date(end_date) if end_date != '' else date_functions.GetToday()
  return database_connection.GetStoreData(discord_id, date_start, date_end)

def GetAllGames():
  games_list = database_connection.GetAllGames()
  games = []
  for game in games_list:
    games.append(tuple_conversions.ConvertToGame(game))

  return games

def GetGame(guild_id, game_name):
  game_name = game_name.upper()
  game_obj = database_connection.GetGame(guild_id, game_name)
  if game_obj is None:
    raise Exception(f'Game {game_name} not found')
  return tuple_conversions.ConvertToGame(game_obj)
  
def GetFormat(guild_id, game, format_name):
  if not game.HasFormats:
    return ''
  format_name = format_name.replace('-',' ').upper()
  format_obj = database_connection.GetFormat(game.ID, format_name)
  if format_obj is None:
    raise Exception(f'Format {format_name} not found')
  return tuple_conversions.ConvertToFormat(format_obj)

def GetEvent(guild_id, event_date, game, format):
  event_obj = database_connection.GetEvent(guild_id, event_date, game, format)
  if event_obj is None:
    return None
  return tuple_conversions.ConvertToEvent(event_obj)
  
def GetAttendance(discord_id,
                  game,
                  format):
  end_date = date_functions.GetToday()
  start_date = date_functions.GetStartDate(end_date)
  game = GetGame(discord_id, game)
  format = GetFormat(discord_id, game, format)
  participation = database_connection.GetAttendance(discord_id,
                                                    game,
                                                    format,
                                                    start_date,
                                                    end_date)
  title = 'Attendance for '
  if game.HasFormats and format is not None:
    title += f'{format.FormatName.title()}'
  else:
    title += f'{game.Name.title()}'
  headers = ['Date', 'Number of Players']
  if discord_id == settings.DATAGUILDID:
    headers.insert(1, 'Store')
  output = output_builder.BuildTableOutput(title, headers, participation)
  return output

def ConvertMessageToParticipants(message):
  data = CompanionParticipants(message)
  if data is None:
    data = MeleeParticipants(message)
  #if data is None:
    #data = CompanionRoundByRound(message)
  return data

def MeleeParticipants(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0,len(rows),3):
      name = ' '.join(rows[i + 1].split(' ')[0:-1])
      record = rows[i + 2].split('    ')[0].split('-')
      wins = record[0]
      losses = record[1]
      draws = record[2]
      participant = tuple_conversions.Participant(name,
                                                  int(wins),
                                                  int(losses),
                                                  int(draws)
                                                 )
      #print('Participant: ', participant)
      data.append(participant)
    return data
  except Exception as exception:
    #print('Rows:', rows)
    #print('Melee Exception:', exception)
    return None

#TODO: Obtain a direct message from a user with the correct source of data to test this structure
def CompanionRoundByRound(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0, len(rows), 4):
      row = " ".join(rows[i:i + 4])
      row = row.replace("\"","")
      row = row.split('  ')
      p1name = ' '.join(row[4].split(' ')[0:-1])
      p1gw = row[6].split(' ')[0]
      p2gw = row[6].split(' ')[1]
      p2name = ' '.join(row[8].split(' ')[0:-1])
      result = tuple_conversions.Round(p1name, int(p1gw), p2name, int(p2gw))
      print('Result:', result)
      data.append(result)
    return data
  except Exception as exception:
    print('Rows:', rows)
    print('Companion Round Exception:', exception)
    return None

def CompanionParticipants(message):
  data = []
  rows = message.split('\n')
  try:
    for row in rows:
      row_list = row.split('    ')
      
      #print('Row List:', row_list)
      int(row_list[0])
      int(row_list[2])
      record = row_list[3].split('/')
      participant = tuple_conversions.Participant(row_list[1],
                                                  int(record[0]),
                                                  int(record[1]),
                                                  int(record[2])
                                                 )
      data.append(participant)

    return data  
  except Exception as exception:
    #print('Rows:', rows)
    #print('Companion Exception:', exception)
    return None


def AddGameMap(discord_id,
               game_id,
               used_name):
  rows = database_connection.AddGameMap(discord_id, game_id, used_name.upper())
  if rows is None:
    return None
  game = GetGame(discord_id, used_name)
  return f'Success! {used_name.title()} is now mapped to {game.Name.title()}'

def CreateEvent(date_of_event,
                discord_id,
                game,
                format):
  event_obj = database_connection.CreateEvent(date_of_event, discord_id, game, format)
  event = tuple_conversions.ConvertToEvent(event_obj)
  return event

def AddResults(event_id, data, submitterId):
  successes = 0

  #TODO: This should use polymorphism to make the code more readable
  if isinstance(data[0], tuple_conversions.Participant):
    for person in data:
      output = database_connection.AddResult(event_id, person, submitterId)
      if output:
        successes += 1
  
    return f'{successes} entries were added. Feel free to use /claim and update the archetypes!'
  elif isinstance(data[0], tuple_conversions.Round):
    print('Data is for rounds')
    round_number = (database_connection.GetRoundNumber(event_id) or 0) + 1
    print('Round number:', round_number)
    for round in data:
      result = None
      if round.P1Wins > round.P2Wins:
        result = Winner.PLAYER1
      elif round.P2Wins > round.P1Wins:
        result = Winner.PLAYER2
      else:
        result = Winner.TIE

      player1id = database_connection.GetParticipantId(event_id, round.P1Name.upper())
      player2id = database_connection.GetParticipantId(event_id, round.P2Name.upper())

      if player1id is None:
        person = tuple_conversions.Participant(round.P1Name.upper(), 0, 0, 0)
        player1id = database_connection.AddResult(event_id, person, submitterId)
        
      if player2id is None:
        person = tuple_conversions.Participant(round.P2Name.upper(), 0, 0, 0)
        player2id = database_connection.AddResult(event_id, person, submitterId)

      #increase each player's wins, losses, and draws by 1 where appropriate
      if result == Winner.PLAYER1:
        database_connection.Increase(player1id, 1, 0, 0)
        database_connection.Increase(player2id, 0, 1, 0)
        database_connection.AddRoundResult(event_id, round_number, player1id, player2id, player1id)
      elif result == Winner.PLAYER2:
        database_connection.Increase(player2id, 1, 0, 0)
        database_connection.Increase(player1id, 0, 1, 0)
        database_connection.AddRoundResult(event_id, round_number, player1id, player2id, player2id)
      elif result == Winner.TIE:
        database_connection.Increase(player1id, 0, 0, 1)
        database_connection.Increase(player2id, 0, 0, 1)
        database_connection.AddRoundResult(event_id, round_number, player1id, player2id, None)

    return f'{len(data)} entries were added. Feel free to use /claim and update the archetypes!'

def Claim(date,
          game_name,
          format_name,
          player_name,
          archetype_played,
          updater_id,
          updater_name,
          store_discord):
  game = GetGame(store_discord, game_name)
  format = GetFormat(store_discord, game, format_name)
  event = GetEvent(store_discord, date, game, format)
  output = database_connection.Claim(event.ID,
                                     player_name,
                                     archetype_played,
                                     updater_id)
  if output is None:
    raise Exception(f'{player_name} was not found in that event. The name should match what was put into Companion')
  database_connection.TrackInput(store_discord,
                                 updater_name.upper(),
                                 updater_id,
                                 archetype_played,
                                 date_functions.GetToday(),
                                 player_name.upper())
  

def GetTopPlayers(discord_id, game_name, format_name, year, quarter, top_number):
  date_range = date_functions.GetQuarterRange(year, quarter)
  start_date = date_range[0]
  end_date = date_range[1]

  game = GetGame(discord_id, game_name)
  format = GetFormat(discord_id, game, format_name)

  store_obj = database_connection.GetStores(discord_id=discord_id)
  store = tuple_conversions.ConvertToStore(store_obj[0])
  results = database_connection.GetTopPlayers(store.DiscordId, game.ID, format, start_date, end_date, top_number)
  title = f'Top {top_number} '
  if format != '':
    title += f'{format.FormatName.title()} '
  title += f'Players For Your Store from {start_date} to {end_date}'

  headers = ('Name', 'Metagame %', 'Win %', 'Combined %')

  return output_builder.BuildTableOutput(title, headers, results)

def GetStore(discord_id):
  results = database_connection.GetStores(discord_id = discord_id)
  if results is None or len(results) == 0:
    return None
  return tuple_conversions.ConvertToStore(results[0])


def ApproveStore(discord_id):
  store_obj = database_connection.SetStoreTrackingStatus(True, discord_id)
  if store_obj is None:
    raise Exception(f'No store found with discord id {discord_id}')
  store = tuple_conversions.ConvertToStore(store_obj)
  return store
  

def DisapproveStore(discord_id):
  store_obj = database_connection.SetStoreTrackingStatus(False, discord_id)
  store = tuple_conversions.ConvertToStore(store_obj)
  return store

def Demo():
  #Deletes my test store and its events in the database so I can offer a live update
  database_connection.DeleteDemo()

  #Event IDs and the weeks before today that they happened
  ids = [
    (29, 10),
    (30, 9),
    (31, 8),
    (32, 7),
    (33, 6),
    (34, 5),
    (35, 4),
    (36, 4),
    (37, 3),
    (38, 2),
    (39, 1),
    (40, 1),
  ]
  for id in ids:
    date = date_functions.GetEventDate(id[1])
    database_connection.UpdateDemo(id[0], date)

def GetMetagame(discord_id, game_name, format_name, start_date, end_date):
  output = ''
  end_date = date_functions.convert_to_date(end_date) if end_date != '' else date_functions.GetToday()
  start_date = date_functions.convert_to_date(start_date) if start_date != '' else date_functions.GetStartDate(end_date)
  game = GetGame(discord_id, game_name)
  if game is None:
    return f'Game {game_name} not found. Please map a game first'
  format = None
  if game.HasFormats:
    format = GetFormat(discord_id, game, format_name)
    if format is None:
      return f'Format {format_name} not found'
  
  title_name = format.FormatName.title() if format else game.Name.title()
  metagame = database_connection.GetDataRowsForMetagame(game,
                                                        format,
                                                        start_date,
                                                        end_date,
                                                        discord_id)
  if len(metagame) == 0:
    output = 'No data found'
  else:
    title = f'{title_name} metagame from {start_date} to {end_date}'
    
    headers = ['Deck Archetype', 'Meta % ', 'Win %  ', 'Combined %']
    output = output_builder.BuildTableOutput(title, headers, metagame)
  return output


def RegisterStore(discord_id,
                 discord_name,
                 store_name,
                 owner_id,
                 owner_name):
  store_obj = database_connection.RegisterStore(discord_id,
                                                discord_name,
                                                store_name,
                                                owner_id,
                                                owner_name)
  return tuple_conversions.ConvertToStore(store_obj)
  
