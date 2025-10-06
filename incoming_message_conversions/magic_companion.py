from custom_errors import KnownError
from tuple_conversions import Standing, Pairing
from collections import namedtuple

Result = namedtuple('Result', ['Data', 'Errors'])


def CompanionStandings(message, seperator):
  data = []
  errors = []
  rows = message.split('\n')

  for i in range(0, len(rows)):
    try:
      row_list = rows[i].split(seperator)

      player_name = row_list[1]

      record = row_list[3].split('/')
      wins = int(record[0])
      if wins < 0:
        raise KnownError(f'Wins cannot be negative for row {i + 1}: {rows[i]}')
      losses = int(record[1])
      if losses < 0:
        raise KnownError(f'Losses cannot be negative for row {i + 1}: {rows[i]}')
      draws = int(record[2])
      if draws < 0:
        raise KnownError(f'Draws cannot be negative for row {i+1}: {rows[i]}')

      player = Standing(player_name, wins, losses, draws)
      data.append(player)
    except ValueError:
      errors.append(f'Unable to parse the record for row {i+1}: {rows[i]}')
    except KnownError as exception:
      errors.append(exception.message)
    except Exception:
      errors.append(f'Unable to parse row {i+1}: {rows[i]}')

  return Result(data if len(data) > 0 else None, errors)

def CompanionPairings(message):
  data = []
  errors = []
  rows = message.split('\n')
  for i in range(0, len(rows), 6):
    row = rows[i:i + 6]
    try:
      if row[3].upper() != 'Bye'.upper():
        p1name = row[1]
        if p1name == '':
          raise KnownError(f'Names cannot be blank (row {i + 2}, please resubmit rows {i + 1} - {i + 6})')
        p1gw = int(row[3][0])
        p2gw = int(row[3][1])
        if p1gw > 2 or p2gw > 2 or p1gw + p2gw >= 4:
          raise KnownError(f'Game wins cannot be greater than 2 and cannot add up to 4 or more (row {i + 4}: "{rows[i + 3]}", please resubmit rows {i + 1} - {i + 6})')
        p2name = row[4]
        if p2name == '':
          raise KnownError(f'Names cannot be blank (row {i + 5}, please resubmit rows {i + 1} - {i + 6})')
        roundnumber = int(row[2][0]) + int(row[2][2]) + int(row[2][4])
        #result = Pairing(p1name, p1gw, p2name, p2gw, roundnumber)
        #data.append(result)
      else:
        p1name = row[0]
        if p1name == '':
          raise KnownError(f'Names cannot be blank (row {i + 1}, please resubmit rows {i + 1} - {i + 4})')
        p1gw = 2
        p2name = 'Bye'
        p2gw = 0
        roundnumber = int(row[1][0]) + int(row[1][2]) + int(row[1][4])
      result = Pairing(p1name, p1gw, p2name, p2gw, roundnumber)
      data.append(result)
    except ValueError:
      errors.append(f'Unable to parse the record for row {i + 4}: {rows[i + 3]}')
    except KnownError as exception:
      errors.append(exception.message)
    except Exception:
      errors.append(f'Unable to parse result (rows {i + 1} - {i + 6})')

  return Result(data if len(data) > 0 else None, errors)
