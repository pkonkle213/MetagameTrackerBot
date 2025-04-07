import date_functions

def DiscordInfo(interaction):
  response = []
  currentDateTime = str(date_functions.GetToday())
  response.append(f'Current Date: {currentDateTime}')
  response.append(f'Message Author Name: {str(interaction.user)}')
  response.append(f'Message Author ID: {str(interaction.user.id)}')
  response.append(f'Discord Guild Name: {str(interaction.guild.name)}')
  response.append(f'Discord Guild ID: {str(interaction.guild.id)}')
  response.append(f'Discord Guild Category: {str(interaction.channel.category)}')
  response.append(f'Discord Guild Category ID: {str(interaction.channel.category.id)}')
  response.append(f'Discord Guild Channel: {str(interaction.channel)}')
  response.append(f'Discord Guild Channel ID: {str(interaction.channel.id)}')

  return '\n'.join(response)

def MaxLength(headers, collection):
  buffer = 2
  maxLengths = []
  for header in headers:
    maxLengths.append(len(header) + buffer)
  maxLengths[len(maxLengths) - 1] -= 2

  for item in collection:
    for i in range(len(headers)):
      length = len(str(item[i])) + buffer
      if length > maxLengths[i]:
        maxLengths[i] = length

  return maxLengths

def BuildTableOutput(title,
                     headers,
                     items):
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
      output += column_format.format(element.title())
    output += '\n'

  if len(output) > 1994:
    output = output[:1994] + '...'
  else:
    output = output[:1997]
  output += '```'
  return output