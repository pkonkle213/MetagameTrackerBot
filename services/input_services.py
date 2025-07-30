import unicodedata

def ConvertInput(oldInput):
  upperCase = oldInput.upper()
  nfkd_form = unicodedata.normalize('NFKD', upperCase)
  combined = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
  finalResult = combined.encode('ascii', 'ignore').decode('ascii')

  return finalResult