import unicodedata

def ConvertName(oldName):
  upperName = oldName.upper()
  nfkd_form = unicodedata.normalize('NFKD', upperName)
  combName = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
  aName = combName.encode('ascii', 'ignore').decode('ascii')

  print('Returning:', aName)
  return aName