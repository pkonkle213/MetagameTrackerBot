import os

import discord
from dotenv.main import load_dotenv

import myCommands
import datefuncs
import newDatabase
import outputBuilder

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def MessageUser(msg, userId):
  user = await client.fetch_user(userId)
  await user.send(f'{msg}')


async def MessageChannel(msg, guildId, channelId):
  server = client.get_guild(int(guildId))
  channel = server.get_channel(int(channelId))
  await channel.send(f'{msg}')


async def ErrorMessage(msg):
  await MessageChannel(msg, GUILDID, ERRORID)


async def ApprovalMessage(msg):
  await MessageChannel(msg, GUILDID, APPROVALID)


@client.event
async def on_ready():
  print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
  if message.author == client.user or not message.content.startswith('$'):
    return

  command = message.content.split()[0].upper()
  output = 'Unrecognized command'
  isPhil = message.author.id == PHILID
  isMyGuild = message.guild.id == GUILDID
  isCBUSMTG = message.guild.id == CBUSID

  store = myCommands.GetStore(message.guild.id)
  storeCanTrack = False
  isSubmitter = False
  isStoreOwner = False
  if store is not None:
    storeCanTrack = store.ApprovalStatus
    isStoreOwner = message.author.id in newDatabase.GetStoreOwners()
    isSubmitter = isStoreOwner or message.author.id in newDatabase.GetSubmitters(
        message.guild.id)

  print(
      f'User {str(message.author)} messaged {message.content} from {str(message.guild)} in {str(message.channel.category)} - {str(message.channel)}'
  )

  if command == '$COMMANDS' or command == '$HELP':
    output = outputBuilder.PrintCommands(storeCanTrack, isSubmitter, isPhil,
                                         isMyGuild, isStoreOwner, isCBUSMTG)

  if isMyGuild:
    if command == '$GETBOT':
      output = MYBOTURL

    if command == '$GETSHEETS':
      output = SHEETSURL

  if command == '$REGISTER':
    result = myCommands.RegisterStore(message)
    if result[0] == 'Success':
      await MessageChannel(result[2], GUILDID, APPROVALID)
      await MessageUser(result[2], PHILID)
    output = result[1]

  #if command == '$FORMATS':
  #  output = myCommands.GetFormats(message)

  if command == '$METAGAME':
    discord_id = message.guild.id
    game = str(message.channel.category.name)
    format = str(message.channel.name)
    msg = message.content.split(' ')
    start_date = ''
    end_date = ''
    if len(msg) > 1:
      start_date = msg[1]
    if len(msg) > 2:
      end_date = msg[2]
    output = myCommands.GetMetagame(discord_id, game, format, start_date,
                                  end_date)

  if (storeCanTrack and isSubmitter) or (isPhil and isMyGuild):
    if command == '$ADDRESULTS':
      results = message.content.split('\n')[1:]
      await message.channel.send(f'Attempting to add {len(results)} results...'
                                 )
      output = myCommands.AddResults(message.guild.id, GUILDID, results,
                                   message.author.id)

  if isMyGuild and isStoreOwner:
    if command == '$EVENTS':
      output = myCommands.FindEvents(message.author.id)

    if command == '$EVENT':
      msg = message.content.split('~')
      date = datefuncs.convert_to_date(msg[1])
      game = msg[2]
      format = msg[3].upper()
      output = myCommands.GetPlayersInEvent(message.author.id, game, date,
                                          format)

    if command == '$UPDATEROW':
      msg = message.content.split('\n')
      output = myCommands.UpdateDataRow(msg[1], msg[2], message.author.id)

    if command == '$TOPPLAYERS':
      msg = message.content.split(' ')
      format = ''
      dateStart = ''
      dateEnd = ''
      if len(msg) > 1:
        format = msg[1]
      if len(msg) > 2:
        dateStart = msg[2]
      if len(msg) > 3:
        dateEnd = msg[3]
      output = myCommands.GetTopPlayers(message.author.id,
                                      'Magic: the gathering',
                                      format=format,
                                      start_date=dateStart,
                                      end_date=dateEnd)

  if isPhil:
    if command == '$TEST':
      info = outputBuilder.DiscordInfo(message)
      await MessageUser(info, PHILID)
      output = 'Information relayed'

    if isMyGuild:
      if command == '$GETALLSTORES':
        output = myCommands.GetStores()

      if command == '$APPROVESTORE':
        store_discord_id = int(message.content.split()[1])
        output = myCommands.ApproveStore(store_discord_id)
        approved_store = newDatabase.GetStores(discord_id=store_discord_id)[0]
        print(approved_store)
        await MessageUser(
            'Congratulations! You\'ve been approved to track your metagame!',
            approved_store[3])

      if command == '$ADDGAMEMAP':
        msg = message.content.split('~')
        used_name = msg[1]
        actual_name = msg[2]
        output = myCommands.AddGameMap(used_name, actual_name)

  if output == '' or output is None:
    await ErrorMessage(f'This request produced no output: {message.content}')
    output = 'Something went wrong and there was no output. This has been reported'
  await message.channel.send(output)


load_dotenv()
SHEETSURL = os.getenv('SHEETSURL')
MYBOTURL = os.getenv('MYBOTURL')
PHILID = int(os.getenv('PHILID'))
CBUSID = int(os.getenv('COLUMBUSGUILDID'))
GUILDID = int(os.getenv('BOTGUILDID'))
ERRORID = int(os.getenv('BOTERRORCHANNELID'))
APPROVALID = int(os.getenv('BOTAPPROVALCHANNELID'))
client.run(os.getenv('DISCORDTOKEN'))
