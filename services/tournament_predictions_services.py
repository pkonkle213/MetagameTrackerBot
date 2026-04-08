import math

def NumRounds(players: int) -> int:
  """Predicts the number of rounds in a tournament"""
  if players < 1:
    raise Exception("Number of players must be greater than 0")
  return math.ceil(math.log(players, 2))

def PredictTop8(num_players:int, rounds: int) -> str:
  """Predicts the top 8 records in a tournament"""
  print('Rounds:', rounds)
  
  players = 0
  records = {}
  losses = 0
  while players < 8:
    wins = rounds - losses
    print('Rounds:', rounds, 'Wins:', wins)
    rec_players = round(math.comb(rounds, wins) * .5**wins * .5**losses * num_players)
    
    if players + rec_players < 8:
      players += rec_players
    else:
      rec_players = 8 - players
      players = 8
    
    records[f"{losses}"] = {"players": rec_players, "record": f"{wins} - {losses}"}
    losses += 1

  output = ''
  for key in records:
    players = records[key]['players']
    record = records[key]['record']
    output += f"{players} player{'s' if players > 1 else ''} with a {record} record\n"
    
  return output

def PredictMyTop8(user_id:int, players:int, rounds:int) -> float:
  """Predicts the probability of a player making top 8 based upon their win %"""
  return 1.0