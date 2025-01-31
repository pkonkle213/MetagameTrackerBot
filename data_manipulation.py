import date_functions
import database_connection
import output_builder
import tuple_conversions

def ConvertMessageToParticipants(rows):
  data = []
  try:
    for row in rows:
      row_list = row.split('    ')
      int(row_list[0])
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


def GetEvent(date_of_event, discord_id, game, format):
  event_obj = database_connection.GetEvent(discord_id, date_of_event, game, format)
  event = tuple_conversions.ConvertToEvent(event_obj)
  return event


def Claim(event_id,
          player_name,
          archetype_played,
          updater_id,
          updater_name,
          store_discord):
  output = database_connection.Claim(event_id,
                                     player_name,
                                     archetype_played,
                                     updater_id)
  database_connection.TrackInput(store_discord,
                                 updater_name.upper(),
                                 updater_id,
                                 archetype_played,
                                 date_functions.GetToday(),
                                 player_name.upper())
  return output == 'Success'
  

def GetTopPlayers(discord_id, game, format, year, quarter, top_number):
  date_range = date_functions.GetQuarterRange(year, quarter)
  start_date = date_range[0]
  end_date = date_range[1]

  game_obj = database_connection.GetGame(discord_id, game)
  format_obj = database_connection.GetFormat(game_obj[0], format)

  store_obj = database_connection.GetStores(discord_id=discord_id)
  store = tuple_conversions.ConvertToStore(store_obj[0])
  results = database_connection.GetTopPlayers(store.DiscordId, game_obj[0], format_obj[0], start_date, end_date, top_number)
  top_players = tuple_conversions.ChangeDataRowsToLeaderBoard(results)
  title = f'Top {top_number} Players for {store.StoreName.title()} '
  if format != '':
    title += f'in {format.title()} '
  title += f'from {start_date} to {end_date}'

  headers = ('Name', 'Metagame %', 'Win %', 'Combined %')

  return output_builder.BuildTableOutput(title, headers, top_players)

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


def GetMetagame(discord_id, game, format, start_date, end_date):
  output = ''
  end_date = date_functions.convert_to_date(end_date) if end_date != '' else date_functions.GetToday()
  start_date = date_functions.convert_to_date(start_date) if start_date != '' else date_functions.GetStartDate(end_date)
  metagame = database_connection.GetDataRowsForMetagame(game[0],
                                                        format[0],
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
  store = tuple_conversions.Store(discord_id,
                                  discord_name,
                                  store_name,
                                  owner_id,
                                  owner_name,
                                  False)
  
  database_connection.AddStore(store)
  output = (
        'Success',
        f'{store.StoreName.title()} added to the database, welcome! Please see Phillip for tracking approval',
        f'{store.StoreName.title()} has registered to track their data. DiscordId: {store.DiscordId}'
    )

  return output
