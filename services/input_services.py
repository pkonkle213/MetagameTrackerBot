import unicodedata

#TODO: This should be called ConvertString as it should affect archetypes submitted as well
def ConvertInput(oldInput):
  upperCase = oldInput.upper()
  nfkd_form = unicodedata.normalize('NFKD', upperCase)
  combined = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
  finalResult = combined .encode('ascii', 'ignore').decode('ascii')

  return finalResult