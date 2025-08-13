from data.demonstration_data import DeleteDemo, UpdateDemo
from services.date_functions import GetToday, GetWeeksAgo

def NewDemo():
  #Deletes my test store events in the database so I can offer a live update
  DeleteDemo()

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
    today = GetToday()
    date = GetWeeksAgo(today, id[1])
    UpdateDemo(id[0], date)