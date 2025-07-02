import unicodedata

#TODO: This should be called ConvertString as it should affect archetypes submitted as well
def ConvertName(oldName):
  upperName = oldName.upper()
  nfkd_form = unicodedata.normalize('NFKD', upperName)
  combName = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
  aName = combName.encode('ascii', 'ignore').decode('ascii')

  return aName