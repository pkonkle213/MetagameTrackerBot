from database_connection import DeleteDemo, UpdateDemo
import date_functions

def NewDemo():
  #Deletes my test store and its events in the database so I can offer a live update
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
    today = date_functions.GetToday()
    date = date_functions.GetWeeksAgo(today, id[1])
    UpdateDemo(id[0], date)