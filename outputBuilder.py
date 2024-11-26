import datetime
import pytz

def PrintCommands(canTrack,
                  canSubmit,
                  isPhil,
                  isMyGuild,
                  isStoreOwner,
                  isCBUSMTG):
  responses = []
  isPhil = False

  responses.append('Here are my current commands:')

  if isMyGuild:
    responses.append('`$bot` - Displays the link to this bot')
    responses.append('`$sheets` - Displays the link to the Google Sheets companion')

    if False and isPhil:
      responses.append('`$approveStore` `storeDiscordId` - Approves a store to track')
      responses.append('`$revokeApproval` `storeDiscordId` - Takes away a store\'s approval to track')
      responses.append('`$getAllStores` - Displays all stores in the database')

    if isStoreOwner:
      responses.append('`$addSubmitter` `user_id` - Adds a user to your allowed submitter list')
      responses.append('`$deleteSubmitter` `user_id` - removes a user from the submitter list')
      responses.append('`$myEvents` - View your store\'s events')
      responses.append('`$seeEvent` ~`date`~`game`~`format` - View the players in an event')
      responses.append('`$topPlayers` `format` - Displays the top players for a given format in the current quarter year')
      responses.append('`$topPlayers` `format` `startDate` `endDate` - Displays the top players for a given format in the given date range')
      responses.append('`$updateDataRow` followed by a list of properly formatted strings will update a datarow')

  elif isCBUSMTG:
    responses.append('Soon to come!')
    #responses.append('`$metagame` `storeName` - Displays the metagame for the format channel you\'re in for the past 8 weeks')
  else:
    if isPhil:
      responses.append('`$test` - Sends details to me concerning the discord guild, channel, category, etc')

    if not canTrack:
      responses.append('`$register` `storeName` - Register a store to track and an owner for the store')
    else:
      responses.append('`$metagame` - Prints a table for the channel\'s metagame')
      responses.append('`$metagame` `startDate` `endDate` - Similar but for a date range')
      if canSubmit:
        responses.append('`$addResults` followed by a list of properly formatted strings will add event data to the database')

  response = '\n'.join(responses)
  return response

def MaxLength(headers, collection):
  buffer = 2
  maxLengths = []
  for header in headers:
    maxLengths.append(len(header) + buffer)

  for item in collection:
    for i in range(len(headers)):
      if len(str(item[i])) + buffer > maxLengths[i]:
        maxLengths[i] = len(str(item[i])) + buffer

  return maxLengths

def DiscordInfo(interaction):
  response = []
  currentDateTime = str(datetime.datetime.now(pytz.timezone('US/Eastern')).date())
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
      column_format = '{:' + align + str(column_widths[i]) + 's}'
      output += column_format.format(str(item[i]).title())
      output = output.strip() #TODO: Double check this is good
    output += '\n'

  if len(output) > 1994:
    output = output[:1994] + '...'
  else:
    output = output[:1997]
  output += '```'
  return output