import unicodedata

def ConvertInput(oldInput:str) -> str:
  trimmed = oldInput.strip().replace("'","")
  nfkd_form = unicodedata.normalize('NFKD', oldInput)
  combined = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
  finalResult = combined.encode('ascii', 'ignore').decode('ascii')

  return finalResult