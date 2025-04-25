import date_functions
import database_connection
import output_builder
import settings
import tuple_conversions
import spicerack
from enum import Enum, auto


class Winner(Enum):
  TIE = auto()
  PLAYER1 = auto()
  PLAYER2 = auto()


def GetSpicerackData(discord_id, event_id):
  store_obj = database_connection.GetStores(discord_id=discord_id)
  if store_obj is None:
    raise Exception('Store not found')
  store = tuple_conversions.ConvertToStore(store_obj[0])
  #Check that the event_id hasn't been submitted yet
  spicerack_id = database_connection.GetSpiceId(event_id)
  if spicerack_id:
    return 'This event has already been submitted'

  #Get the event data from spicerack
  data = spicerack.GetEventData(store.DiscordId, event_id)

  event = GetEvent(discord_id, date_of_event, game, format)
  if event is None:
    event = CreateEvent(date_of_event, message.guild.id, game, format)

  output = AddResults(event_id, data, store.OwnerId, event_id)

  #import the data into the database
  #report the results
  output = 'Success??'
  return output


def InteractionData(interaction):
  discord_id = interaction.guild.id
  game_name = interaction.channel.category.name
  game = GetGame(discord_id, game_name)
  if game.HasFormats:
    format_name = interaction.channel.name
    format = GetFormat(discord_id, game, format_name)
  else:
    format = None

  return tuple_conversions.InteractionDetails(game, format,
                                              interaction.guild.id,
                                              interaction.channel.id,
                                              interaction.user.id)


def GetWLDStat(discord_id, game_name, format_name, user_id, start_date,
               end_date):
  game = GetGame(discord_id, game_name)
  format = GetFormat(discord_id, game, format_name)
  end_date = date_functions.convert_to_date(
      end_date) if end_date != '' else date_functions.GetToday()
  start_date = date_functions.convert_to_date(
      start_date) if start_date != '' else date_functions.GetStartDate(
          end_date)
  try:
    data = database_connection.GetStats(discord_id, game.ID, format.ID,
                                        user_id, start_date, end_date)
  except Exception as exception:
    return str(exception)
  title = f'Your Play Record from {str(start_date)} to {str(end_date)}'
  header = ['Archetype Name', 'Wins', 'Losses', 'Draws', 'Win %']
  output = output_builder.BuildTableOutput(title, header, data)
  return output


#Need to update this for games that don't have formats yet
def GetAnalysis(discord_id, game_name, format_name, weeks):
  game = GetGame(discord_id, game_name)
  format = GetFormat(discord_id, game, format_name)

  if game is None or (game.HasFormats and format is None):
    raise Exception('Insufficient information provided')

  #Uncomment to fake data
  #Comment to use true data
  discord_id = settings.TESTSTOREGUILD.id
  game = tuple_conversions.ConvertToGame((1, "Magic", True))
  format = tuple_conversions.ConvertToFormat((1, "Pauper"))

  dates = date_functions.GetAnalysisDates(weeks)
  data = database_connection.GetAnalysis(discord_id, game.ID, format.ID, weeks,
                                         True, dates)
  #If the True/False values flex the sql, it needs to flex the title and headers as well
  title = f'Percentage Shifts in Meta from {dates[3]} to {dates[0]}'
  headers = [
      'Archetype', 'First Half Meta %', 'Second Half Meta %', 'Meta % Shift'
  ]
  output = output_builder.BuildTableOutput(title, headers, data)
  return output


def GetDataReport(discord_id, start_date, end_date):
  start = start_date if start_date != '' else '1/1/2024'
  date_start = date_functions.convert_to_date(start)
  date_end = date_functions.convert_to_date(
      end_date) if end_date != '' else date_functions.GetToday()
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
  format_name = format_name.replace('-', ' ').upper()
  format_obj = database_connection.GetFormat(game.ID, format_name)
  if format_obj is None:
    raise Exception(f'Format {format_name} not found')
  return tuple_conversions.ConvertToFormat(format_obj)


def GetEvent(guild_id, event_date, game, format):
  event_obj = database_connection.GetEvent(guild_id, event_date, game, format)
  if event_obj is None:
    return None
  return tuple_conversions.ConvertToEvent(event_obj)


def GetAttendance(discord_id, game, format):
  end_date = date_functions.GetToday()
  start_date = date_functions.GetStartDate(end_date)
  game = GetGame(discord_id, game)
  format = GetFormat(discord_id, game, format)
  participation = database_connection.GetAttendance(discord_id, game, format,
                                                    start_date, end_date)
  title = 'Attendance for '
  if game.HasFormats and format is not None:
    title += f'{format.FormatName.title()}'
  else:
    title += f'{game.Name.title()}'
  headers = ['Date', 'Players']
  if discord_id == settings.DATAGUILDID:
    headers.insert(1, 'Store')
  output = output_builder.BuildTableOutput(title, headers, participation)
  return output


def ConvertMessageToParticipants(message):
  #TODO: Use polymorphism to make this more generic
  data = CompanionParticipants(message)
  if data is None:
    data = MeleeParticipants(message)
  '''
  if data is None:
    data = CompanionRoundByRound(message)
  '''
  return data


def MeleeParticipants(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0, len(rows), 3):
      name = ' '.join(rows[i + 1].split(' ')[0:-1])
      record = rows[i + 2].split('    ')[0].split('-')
      wins = record[0]
      losses = record[1]
      draws = record[2]
      participant = tuple_conversions.Participant(name, int(wins), int(losses),
                                                  int(draws))
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
    for i in range(0, len(rows), 6):
      row = rows[i:i + 6]
      print('Raw row:', row)
      #This issue that if the last row is a bye, this breaks
      #row[3]=='Bye'
      p1name = row[1]
      p1gw = row[3][0]
      p2gw = row[3][1]
      p2name = row[4]
      result = tuple_conversions.Round(p1name, int(p1gw), p2name, int(p2gw))
      print('Result:', result)
      data.append(result)
    return data
  except Exception as exception:
    print('Rows:', rows)
    print('Companion Round Exception:', exception)
    return None


def SheetsParticipants(message):
  ...


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
      participant = tuple_conversions.Participant(row_list[1], int(record[0]),
                                                  int(record[1]),
                                                  int(record[2]))
      data.append(participant)

    return data
  except Exception as exception:
    #print('Rows:', rows)
    #print('Companion Exception:', exception)
    return None


def AddGameMap(discord_id, game_id, used_name):
  rows = database_connection.AddGameMap(discord_id, game_id, used_name.upper())
  if rows is None:
    return None
  game = GetGame(discord_id, used_name)
  return f'Success! {used_name.title()} is now mapped to {game.Name.title()}'


def CreateEvent(date_of_event, discord_id, game, format):
  event_obj = database_connection.CreateEvent(date_of_event, discord_id, game,
                                              format)
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

      player1id = database_connection.GetParticipantId(event_id,
                                                       round.P1Name.upper())
      player2id = database_connection.GetParticipantId(event_id,
                                                       round.P2Name.upper())

      if player1id is None:
        person = tuple_conversions.Participant(round.P1Name.upper(), 0, 0, 0)
        player1id = database_connection.AddResult(event_id, person,
                                                  submitterId)

      if player2id is None:
        person = tuple_conversions.Participant(round.P2Name.upper(), 0, 0, 0)
        player2id = database_connection.AddResult(event_id, person,
                                                  submitterId)

      #increase each player's wins, losses, and draws by 1 where appropriate
      if result == Winner.PLAYER1:
        database_connection.Increase(player1id, 1, 0, 0)
        database_connection.Increase(player2id, 0, 1, 0)
        database_connection.AddRoundResult(event_id, round_number, player1id,
                                           player2id, player1id)
      elif result == Winner.PLAYER2:
        database_connection.Increase(player2id, 1, 0, 0)
        database_connection.Increase(player1id, 0, 1, 0)
        database_connection.AddRoundResult(event_id, round_number, player1id,
                                           player2id, player2id)
      elif result == Winner.TIE:
        database_connection.Increase(player1id, 0, 0, 1)
        database_connection.Increase(player2id, 0, 0, 1)
        database_connection.AddRoundResult(event_id, round_number, player1id,
                                           player2id, None)

  return f'{len(data)} entries were added. Feel free to use /claim and update the archetypes!'


def Claim(date, game_name, format_name, player_name, archetype_played,
          updater_id, updater_name, store_discord):
  game = GetGame(store_discord, game_name)
  if game is None:
    raise Exception('Game not found')
  format = GetFormat(store_discord, game, format_name)
  if game.HasFormats and format is None:
    raise Exception('Format not found')
  event = GetEvent(store_discord, date, game, format)
  if event is None:
    raise Exception('Event not found')
  claimed = database_connection.Claim(event.ID, player_name, archetype_played,
                                      updater_id)
  if claimed is None:
    raise Exception(
        f'{player_name} was not found in that event. The name should match what was put into Companion'
    )
  database_connection.TrackInput(store_discord, event.ID, updater_name.upper(),
                                 updater_id, archetype_played,
                                 date_functions.GetToday(),
                                 player_name.upper())
  #get the % of archetypes that aren't 'UNKNOWN' and the event's last_update
  #if % > last_update / 4, update last_update and return message
  percent_reported = database_connection.GetPercentage(event.ID)

  #TODO: If the submission makes it 100%, this is still true, maybe there should be a work around??
  if percent_reported >= (event.LastUpdate + 1) / 4:
    database_connection.UpdateEvent(event.ID)
    if event.LastUpdate + 1 < 4:
      return f'Congratulations! The {date_functions.FormatDate(event.EventDate)} event is now {percent_reported:.0%} reported!'
    else:
      str_date = date_functions.FormatDate(event.EventDate)
      output = f'Congratulations! The {str_date} event is now fully reported! Thank you to all who reported their archetypes!\n\n'
      database_connection.UpdateEvent(event.ID)
      event_meta = database_connection.GetEventMeta(event.ID)
      output += output_builder.BuildTableOutput(f'{str_date} Meta',
                                                ['Archetype', 'Wins'],
                                                event_meta)
      return output
  return None


def GetTopPlayers(discord_id, game_name, format_name, year, quarter,
                  top_number):
  date_range = date_functions.GetQuarterRange(year, quarter)
  start_date = date_range[0]
  end_date = date_range[1]

  game = GetGame(discord_id, game_name)
  format = GetFormat(discord_id, game, format_name)

  store_obj = database_connection.GetStores(discord_id=discord_id)
  store = tuple_conversions.ConvertToStore(store_obj[0])
  results = database_connection.GetTopPlayers(store.DiscordId, game.ID, format,
                                              start_date, end_date, top_number)
  title = f'Top {top_number} '
  if format != '':
    title += f'{format.FormatName.title()} '
  title += f'Players from {start_date} to {end_date}'

  headers = ['Name', 'Attendance %', 'Win %', 'Combined %']
  return output_builder.BuildTableOutput(title, headers, results)


def GetStore(discord_id):
  results = database_connection.GetStores(discord_id=discord_id)
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
      (1, 10),
      (2, 9),
      (3, 8),
      (4, 7),
      (5, 6),
      (6, 5),
      (7, 4),
      (8, 4),
      (9, 3),
      (10, 2),
      (11, 1),
      (12, 1),
  ]
  for id in ids:
    today = date_functions.GetToday()
    date = date_functions.GetWeeksAgo(today, id[1])
    database_connection.UpdateDemo(id[0], date)


def DetermineDates(start_date, end_date, format):
  if format.ID == 15:
    return date_functions.GetQuarterRange(0, 0)
  else:
    edate = date_functions.convert_to_date(
        end_date) if end_date != '' else date_functions.GetToday()
    #TODO: This should check the format's last ban update date and use that instead of the 8 week date if it's later
    if start_date != '':
      sdate = date_functions.convert_to_date(start_date)
    else:
      sdate = date_functions.GetStartDate(edate)
      if format is not None:
        btuple = database_connection.GetBanDate(format.ID)
        if btuple is not None:
          bdate = btuple[0]
          if bdate > sdate:
            sdate = bdate
    return (sdate, edate)


def GetMetagame(discord_id, game_name, format_name, start_date, end_date):
  output = ''

  game = GetGame(discord_id, game_name)
  if game is None:
    return f'Game {game_name} not found. Please map a game first'
  format = None
  if game.HasFormats:
    format = GetFormat(discord_id, game, format_name)
    if format is None:
      return f'Format {format_name} not found'

  (start_date, end_date) = DetermineDates(start_date, end_date, format)

  title_name = format.FormatName.title() if format else game.Name.title()
  metagame = database_connection.GetDataRowsForMetagame(
      game, format, start_date, end_date, discord_id)
  if len(metagame) == 0:
    output = 'No data found'
  else:
    title = f'{title_name} metagame from {start_date} to {end_date}'

    headers = ['Deck Archetype', 'Meta %', 'Win %', 'Combined %']
    output = output_builder.BuildTableOutput(title, headers, metagame)
  return output


def RegisterStore(discord_id, discord_name, store_name, owner_id, owner_name):
  store_obj = database_connection.RegisterStore(discord_id, discord_name,
                                                store_name, owner_id,
                                                owner_name)
  return tuple_conversions.ConvertToStore(store_obj)
