def MaxLength(headers, collection):
  buffer = 2
  maxLengths = []
  for header in headers:
    maxLengths.append(len(header) + buffer)

  for item in collection:
    for i in range(len(headers)):
      length = len(str(item[i])) + buffer
      if length > maxLengths[i]:
        maxLengths[i] = length

  maxLengths[len(maxLengths) - 1] -= 2
  return maxLengths

def BuildTableOutput(title,
                     headers,
                     items,
                     limited_format = False):
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
      if i == 0 and limited_format:
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