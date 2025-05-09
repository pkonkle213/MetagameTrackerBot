import date_functions
import database_connection
import output_builder
from tuple_conversions import Participant

def ConvertMessageToParticipants(message):
  #TODO: Can I use polymorphism to make this more readable?
  data = CompanionParticipants(message)
  if data is None:
    data = MeleeParticipants(message)
  ''' Not implemented yet
  if data is None:
    data = CompanionRoundByRound(message)
  '''
  return data

def CompanionParticipants(message):
  data = []
  rows = message.split('\n')
  try:
    for row in rows:
      row_list = row.split('    ')
      int(row_list[0]) #Standing
      int(row_list[2]) #Points obtained
      record = row_list[3].split('/')
      participant = Participant(row_list[1],
                                                  int(record[0]),
                                                  int(record[1]),
                                                  int(record[2]))
      data.append(participant)
    return data
  except Exception:
    print('Not data from Companion')
    return None

def MeleeParticipants(message):
  data = []
  rows = message.split('\n')
  try:
    for i in range(0, len(rows), 3):
      name = ' '.join(rows[i + 1].split(' ')[0:-1])
      record = rows[i + 2].split('    ')[0].split('-')
      participant = Participant(name,
                                                  int(record[0]),
                                                  int(record[1]),
                                                  int(record[2]))
      data.append(participant)
    return data
  except Exception:
    return None


#TODO: Message from Tom obtained. Need to work around BYE rounds
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
    raise Exception(f'{player_name} was not found in that event. The name should match what was put into Companion')
  #This needs to include claimed[0] (the id of the participant)
  database_connection.TrackInput(store_discord,
                                 event.ID,
                                 updater_name.upper(),
                                 updater_id,
                                 archetype_played,
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


def GetTopPlayerDa(discord_id, game_name, format_name, year, quarter,
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