import date_functions
import database_connection
import output_builder
import tuple_conversions

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
    raise Exception('Event not found')
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
  title = f'Attendance for {game.Name.title()} '
  if format != '':
    title += f'({format.FormatName.title()})'
  headers = ['Date','Number of Players']
  output = output_builder.BuildTableOutput(title, headers, participation)
  return output

def ConvertMessageToParticipants(rows):
  data = []
  try:
    for row in rows:
      row_list = row.split('    ')
      int(row_list[0])
      print('row_list', row_list[-5])
      int(row_list[-5])
      record = row_list[-4].split('/')
      participant = tuple_conversions.Participant(' '.join(row_list[1:-5]),
                                                  int(record[0]),
                                                  int(record[1]),
                                                  int(record[2])
                                                 )
      data.append(participant)

    return data  
  except Exception:
    return None


def AddGameMap(discord_id,
               game_id,
               used_name):
  used_name = used_name.upper()
  rows = database_connection.AddGameMap(discord_id, game_id, used_name)
  return f'Success! {used_name.title()} is now mapped to {rows[2].title()}' if rows is not None else None

def CreateEvent(date_of_event,
                discord_id,
                game,
                format):
  event_id = database_connection.CreateEvent(date_of_event, discord_id, game, format)
  return event_id

def AddResults(event_id, participants, submitterId):
  successes = 0

  for person in participants:
    output = database_connection.AddResult(event_id, person, submitterId)
    if output == 'Success':
      successes += 1

  #TODO: Upgrade this to tag those who typically play with the names given
  return f'{successes} entries were added. Feel free to use /claim and update the archetypes!'


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
  print('Received store:', store_obj)
  store = tuple_conversions.ConvertToStore(store_obj)
  return store
  

def DisapproveStore(discord_id):
  store_obj = database_connection.SetStoreTrackingStatus(False, discord_id)
  store = tuple_conversions.ConvertToStore(store_obj)
  return store


def GetMetagame(discord_id, game_name, format_name, start_date, end_date):
  output = ''
  end_date = date_functions.convert_to_date(end_date) if end_date != '' else date_functions.GetToday()
  start_date = date_functions.convert_to_date(start_date) if start_date != '' else date_functions.GetStartDate(end_date)
  game = GetGame(discord_id, game_name)
  format = GetFormat(discord_id, game, format_name)
  metagame = database_connection.GetDataRowsForMetagame(game,
                                                        format,
                                                        start_date,
                                                        end_date,
                                                        discord_id)
  if len(metagame) == 0:
    output = 'No data found'
  else:
    title = f'{format[1].title()} metagame from {start_date} to {end_date}'
    
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
  
