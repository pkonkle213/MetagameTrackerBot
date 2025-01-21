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

#
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

#
def GetEvent(date_of_event, discord_id, game, format):
  event_obj = database_connection.GetEvent(discord_id, date_of_event, game, format)
  event = tuple_conversions.ConvertToEvent(event_obj)
  return event

#
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
  
#
def GetPlayersInEvent(author_id,
                      game,
                      event_date,
                      event_format):
  store_obj = database_connection.GetStores(owner = author_id)[0]
  store = tuple_conversions.ConvertToStore(store_obj)
  game = database_connection.GetGameId(discord_id, game.upper())
  event_date = date_functions.convert_to_date(event_date)
  players_obj = database_connection.GetPlayersInEvent(store.DiscordId,game,event_date,event_format)
  title = f'Players in {game.title()} on {str(event_date)}'
  headers = ['Player Name', 'Archetype Played', 'Wins', 'Losses', 'Draws']
  output = output_builder.BuildTableOutput(title, headers, players_obj)
  return output
#
def FindEvents(discord_id):
  store_obj = database_connection.GetStores(discord_id = discord_id)[0]
  store = tuple_conversions.ConvertToStore(store_obj)
  end_date = date_functions.GetToday()
  start_date = date_functions.GetStartDate(end_date)
  rows = database_connection.GetEvents(store.DiscordId, start_date, end_date)
  if len(rows) == 0:
    return 'No events found'
  else:
    title = f'{store.StoreName.title()}\'s events between {start_date} and {end_date}'
    headers = ['Date', 'Game', 'Format', 'Attended']

    output = output_builder.BuildTableOutput(title, headers, rows)
    return output
#
def GetTopPlayers(discord_id, game, format, year, quarter, top_number):
  date_range = date_functions.GetQuarterRange(year, quarter)
  start_date = date_range[0]
  end_date = date_range[1]

  store_obj = database_connection.GetStores(discord_id=discord_id)
  store = tuple_conversions.ConvertToStore(store_obj[0])
  results = database_connection.GetTopPlayers(store.DiscordId, game, format, start_date, end_date, top_number)
  top_players = tuple_conversions.ChangeDataRowsToLeaderBoard(results)
  title = f'Top {top_number} Players for {store.StoreName.title()} '
  if format != '':
    title += f'in {format.title()} '
  title += f'from {start_date} to {end_date}'

  headers = ('Name', 'Metagame %', 'Win %', 'Combined %')

  return output_builder.BuildTableOutput(title, headers, top_players)
#
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
  
#
def DisapproveStore(discord_id):
  store_obj = database_connection.SetStoreTrackingStatus(False, discord_id)
  store = tuple_conversions.ConvertToStore(store_obj)
  return store
#
def AddError(error, errors):
  if error in errors:
    errors[error] += 1
  else:
    errors[error] = 1
#
def ErrorCheck(discordId, errors):
  stores_tuples = database_connection.GetStores(discord_id=discordId)
  stores_stores = []
  for tup in stores_tuples:
    store = tuple_conversions.ConvertToStore(tup)
    stores_stores.append(store)

  if len(stores_stores) == 0:
    AddError('Store not in database', errors)
    return True

  if not stores_stores[0].ApprovalStatus:
    AddError('This store is not yet tracking its data', errors)
    return True

  return False


#
def GetFormats(discord_id, game):
  results = database_connection.GetFormats(discord_id, game)
  if results == []:
    output = 'No formats found'
  else:
    headers = ['Format Name']
    output = output_builder.BuildTableOutput('Formats for this store', headers,
                                            results)
  return output

def GetMetagame(discord_id, game_id, format_id, start_date, end_date):
  output = ''
  end_date = date_functions.convert_to_date(end_date) if end_date != '' else date_functions.GetToday()
  start_date = date_functions.convert_to_date(start_date) if start_date != '' else date_functions.GetStartDate(end_date)
  #game = database_connection.GetGameId(discord_id, game.upper())
  #format = format.upper()
  metagame_data = database_connection.GetDataRowsForMetagame(game_id,
                                                             format_id,
                                                             start_date,
                                                             end_date,
                                                             discord_id)
  if len(metagame_data) == 0:
    output = 'No data found'
  else:
    title = f'{format_id.title()} metagame from {start_date} to {end_date}'
    metagame = tuple_conversions.ChangeDataToMetagame(metagame_data)
    headers = ['Deck Archetype', 'Meta % ', 'Win %  ', 'Combined %']
    output = output_builder.BuildTableOutput(title, headers, metagame)
  return output

#
def GetStoresByGameFormat(game, format):
  stores = database_connection.GetStoreNamesByGameFormat(game, format)
  headers = ['Event Date','Store Name','Attendance']
  title = 'Stores with this format'
  output = output_builder.BuildTableOutput(title,
                                          headers,
                                          stores)
  return output
#
def GetStores():
  stores = database_connection.GetStores()
  headers = ['StoreName', 'DiscordId', 'DiscordName', 'Owner', 'ApprovalStatus']
  output = output_builder.BuildTableOutput('Data On Stores In Database',
                                          headers, stores)
  return output
  
#
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
