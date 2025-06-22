import unicodedata

def ConvertName(oldName):
  print('oldName:',oldName)
  upperName = oldName.upper()
  print('upper:', upperName)
  nfkd_form = unicodedata.normalize('NFKD', upperName)
  print('nfkd:', nfkd_form)
  combName = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
  print('Combining:', combName)
  aName = combName.encode('ascii', 'ignore').decode('ascii')
  print('Ascii:', aName)

  return aName