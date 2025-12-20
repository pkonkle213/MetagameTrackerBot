from typing import Any

def MaxLength(headers:list[str], collection:list[tuple[Any,...]]) -> list[int]:
  buffer = 2
  maxLengths:list[int] = []
  for header in headers:
    maxLengths.append(len(header) + buffer)

  for item in collection:
    for i in range(len(headers)):
      length = len(str(item[i])) + buffer
      if length > maxLengths[i]:
        maxLengths[i] = length

  maxLengths[len(maxLengths) - 1] -= 2
  return maxLengths

def BuildTableOutput(title:str,
                     headers:list[str],
                     items:list[tuple[Any,...]],
                     archetype_column:int = -1) -> str:
  column_widths = MaxLength(headers, items)
  align = ''
  output = f'```{title}\n\n'

  for header in headers:
    width = '{:' + align + str(column_widths[headers.index(header)]) + 's}'
    output += width.format(header)

  output += '\n' + '-' * sum(column_widths) + '\n'

  for item in items:
    for i in range(len(column_widths)):
      element = str(item[i])
      column_format = '{:' + align + str(column_widths[i]) + 's}'
      if element[0] == '-':
        output = output[:-1]
      if i == archetype_column and element != 'UNKNOWN':
        output += column_format.format(element)
      else:
        output += column_format.format(element.title())
    output += '\n'

  if len(output) > 1994:
    output = output[:1994] + '...'
  else:
    output = output[:1997]
  output += '```'
  return output