import datefuncs
import newDatabase
import outputBuilder
import tupleConversions

def AddGameMap(used_name, actual_name):
  used_name = used_name.upper()
  actual_name = actual_name.upper()
  rows = newDatabase.AddGameMap(used_name, actual_name)
  return 'Success' if rows is not None else 'Error'

def UpdateDataRow(oldDataStr,newDataStr,authorId):
  store_obj = newDatabase.GetStores(owner = authorId)
  if len(store_obj) == 0:
    return 'Error: No store found'
  discordId = tupleConversions.ConvertToStore(store_obj[0]).DiscordId
  oldData = oldDataStr.split('~')
  oldData.insert(1, discordId)
  newData = newDataStr.split('~')
  newData.insert(1, discordId)
  oldDataRow = tupleConversions.ConvertToDataRow(oldData)
  newDataRow = tupleConversions.ConvertToDataRow(newData)

  return newDatabase.UpdateDataRow(oldDataRow, newDataRow, authorId)

def GetStoreOwnerIds():
  return newDatabase.GetStoreOwners()

def GetSubmittersForStore(discord_id):
  return newDatabase.GetSubmitters(discord_id)

def GetPlayersInEvent(author_id,
                      game,
                      event_date,
                      event_format):
  store_obj = newDatabase.GetStores(owner = author_id)[0]
  store = tupleConversions.ConvertToStore(store_obj)
  game = newDatabase.GetGameName(game.upper())
  event_date = datefuncs.convert_to_date(event_date)
  players_obj = newDatabase.GetPlayersInEvent(store.DiscordId,game,event_date,event_format)
  title = f'Players in {game.title()} on {str(event_date)}'
  headers = ['Player Name', 'Archetype Played', 'Wins', 'Losses', 'Draws']
  output = outputBuilder.BuildTableOutput(title, headers, players_obj)
  return output

def FindEvents(discord_id):
  store_obj = newDatabase.GetStores(discord_id = discord_id)[0]
  store = tupleConversions.ConvertToStore(store_obj)
  rows = newDatabase.GetEvents(discord_id = store.DiscordId)
  if len(rows) == 0:
    return 'No events found'
  else:
    title = f'{store.Name.title()}\'s events'
    headers = ['Date', 'Attended']

    output = outputBuilder.BuildTableOutput(title, headers, rows)
    return output

def GetTopPlayers(discord_id, game, format, year, quarter):
  start_date = datefuncs.GetQuarterDate()
  end_date = datefuncs.GetEndDate()
  
  if year != 0 and quarter == 0:
    start_date = datefuncs.convert_to_date(f'01/01/{year}')
    end_date = datefuncs.convert_to_date(f'12/31/{year}')
  elif year !=0 and quarter != 0:
    start_date = datefuncs.convert_to_date(f'01/01/{year}')
    month_past = datefuncs.convert_to_date(f'{3 + 3 * (quarter - 1)}/31/{year}')
    end_date = datefuncs.LastDayPreviousMonth(month_past)
    
  format = format.upper()
  game = newDatabase.GetGameName(game.upper())

  if start_date is None or end_date is None or start_date > end_date:
    return 'Error: Invalid date range '

  store_obj = newDatabase.GetStores(discord_id=discord_id)
  store = tupleConversions.ConvertToStore(store_obj[0])
  results = newDatabase.GetTopPlayers(store.DiscordId, game, format, start_date, end_date)
  top_players = tupleConversions.ChangeDataRowsToLeaderBoard(results)
  title = f'Top Players for {store.Name.title()} '
  if format != '':
    title += f'in {format.title()} '
  title += f'from {start_date} to {end_date}'

  headers = ('Name', 'Metagame %', 'Win %', 'Combined %')

  return outputBuilder.BuildTableOutput(title, headers, top_players)

def GetStore(discord_id):
  results = newDatabase.GetStores(discord_id = discord_id)
  if results is None or len(results) == 0:
    return None
  return tupleConversions.ConvertToStore(results[0])

def ApproveStore(discord_id):
  store_obj = newDatabase.ApproveStoreTrackingStatus(discord_id)
  if store_obj is None:
    raise Exception(f'No store found with discord id {discord_id}')
  store = tupleConversions.ConvertToStore(store_obj)
  return store

def DisapproveStore(discord_id):
  store_obj = newDatabase.RemoveStoreTrackingStatus(discord_id)
  store = tupleConversions.ConvertToStore(store_obj)
  return store

def AddError(error, errors):
  if error in errors:
    errors[error] += 1
  else:
    errors[error] = 1

def ErrorCheck(discordId, errors):
  stores_tuples = newDatabase.GetStores(discord_id=discordId)
  stores_stores = []
  for tup in stores_tuples:
    store = tupleConversions.ConvertToStore(tup)
    stores_stores.append(store)

  if len(stores_stores) == 0:
    AddError('Store not in database', errors)
    return True

  if not stores_stores[0].ApprovalStatus:
    AddError('This store is not yet tracking its data', errors)
    return True

  return False

def AddResults(sending_guild_id, myGuildId, eventResults, submitterId):
  errors = {}

  for result in eventResults:
    row = result.upper().split('~')
    dataRow = None
    if len(row) == 8:
      dataRow = tupleConversions.ConvertToDataRow(
        (datefuncs.convert_to_date(row[0]),
         sending_guild_id,
         newDatabase.GetGameName(row[1]),
         row[2],
         row[3],
         row[4],
         int(row[5]),
         int(row[6]),
         int(row[7]),
         submitterId))
    elif sending_guild_id == myGuildId:
      dataRow = tupleConversions.ConvertToDataRow(
        (datefuncs.convert_to_date(row[0]),
         int(row[1]),
         newDatabase.GetGameName(row[2]),
         row[3],
         row[4],
         row[5],
         int(row[6]),
         int(row[7]),
         int(row[8]),
         submitterId))
    else:
      return 'We have no idea what you sent'

    if not ErrorCheck(dataRow.LocationDiscordId, errors):
      print('Adding datarow')
      row = newDatabase.AddDataRow(dataRow)
      if row is None:
        AddError('Row already exists', errors)

  num_errors = sum(errors.values())
  errorpunct = ':' if num_errors > 1 else '.'
  successes = len(eventResults) - num_errors

  output = f'{successes} entries were added. {num_errors} were skipped{errorpunct}'
  if len(errors) > 0:
    output += '\nErrors: ' + ', '.join(errors.keys())

  return output

def GetFormats(discord_id, game):
  results = newDatabase.GetFormats(discord_id, game)
  if results == []:
    output = 'No formats found'
  else:
    headers = ['Format Name']
    output = outputBuilder.BuildTableOutput('Formats for this store', headers,
                                            results)
  return output

def GetMetagame(discord_id, game, format, start_date, end_date):
  output = ''
  end_date = datefuncs.convert_to_date(end_date) if end_date != '' else datefuncs.GetEndDate()
  start_date = datefuncs.convert_to_date(start_date) if start_date != '' else datefuncs.GetStartDate(end_date)
  game = newDatabase.GetGameName(game.upper())
  format = format.upper()
  metagame_data = newDatabase.GetDataRowsForMetagame(game,
                                                     format,
                                                     start_date,
                                                     end_date,
                                                     discord_id)
  if len(metagame_data) == 0:
    output = 'No data found'
  else:
    title = f'{format.title()} metagame from {start_date} to {end_date}'
    metagame = tupleConversions.ChangeDataToMetagame(metagame_data)
    headers = ['Deck Archetype', 'Meta % ', 'Win %  ', 'Combined %']
    output = outputBuilder.BuildTableOutput(title, headers, metagame)
  return output

def GetStoresByGameFormat(game, format):
  stores = newDatabase.GetStoreNamesByGameFormat(game, format)
  headers = ['Event Date','Store Name','Attendance']
  title = 'Stores with this format'
  output = outputBuilder.BuildTableOutput(title,
                                          headers,
                                          stores)
  return output

def GetStores():
  stores = newDatabase.GetStores()
  headers = ['StoreName', 'DiscordId', 'DiscordName', 'Owner', 'ApprovalStatus']
  output = outputBuilder.BuildTableOutput('Data On Stores In Database',
                                          headers, stores)
  return output

def DeleteStore(discordId):
  return newDatabase.DeleteStore(discordId)

def RegisterStore(message):
  output = ''
  msg = message.content.split(' ')
  if len(msg) < 2:
    output = ('Error', 'Please provide a store name', '')
  else:
    store_name = ' '.join(msg[1:])
    store_name = store_name.strip().upper()
    store = tupleConversions.Store(store_name, message.guild.id,
                                   message.guild.name, message.author.id,
                                   False)

    newDatabase.AddStore(store)
    output = (
        'Success',
        f'{store.Name.title()} added to the database, welcome! Please see Phillip for tracking approval',
        f'{store.Name.title()} has registered to track their data. DiscordId: {store.DiscordId}'
    )

  return output

def AddSubmitter(owner_id, user_id):
  store_obj = newDatabase.GetStores(owner = owner_id)
  if len(store_obj) == 0:
    return 'Error: Store not found'
  store = tupleConversions.ConvertToStore(store_obj[0])
  result = newDatabase.AddSubmitter(store.DiscordId, user_id)
  if result is None:
    return 'Error: This user is already a submitter'
  return 'Success'

def RemoveSubmitter(owner_id, user_id):
  store_obj = newDatabase.GetStores(owner = owner_id)
  if len(store_obj) == 0:
    return 'Error: Store not found'
  store = tupleConversions.ConvertToStore(store_obj[0])
  newDatabase.DeleteSubmitter(store.DiscordId, user_id)
  return 'Success'