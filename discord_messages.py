import discord
import settings

async def MessageUser(bot, msg, userId, file=None):
  user = await bot.fetch_user(userId)
  if file is None:
    await user.send(f'{msg}')
  else:
    await user.send(f'{msg}', file=file)

async def MessageChannel(bot, msg, guildId, channelId):
  server = bot.get_guild(int(guildId))
  if server is None:
    print(f'Server {guildId} not found')
    raise Exception(f'Server {guildId} not found')
  if msg != '':
    channel = server.get_channel(int(channelId))
    if channel is None:
      print(f'Channel {channelId} not found')
      raise Exception(f'Channel {channelId} not found')
    if not isinstance(channel, discord.TextChannel):
      raise Exception(f'Channel {channelId} is not a text channel')

    await channel.send(f'{msg}')

async def ErrorMessage(bot, message):
  await MessageChannel(bot,
                       message,
                       settings.BOTGUILD.id,
                       settings.ERRORCHANNELID)

async def Error(bot, error:Exception):
  message =  f"Line number: {error.__traceback__.tb_lineno}"
  message += f"\nFile: {error.__traceback__.tb_frame.f_code.co_filename}"
  message += f"\nLine: {error.__traceback__}"
  message += f"\nError: {error}"
  message += f"\nError type: {type(error)}"
  message += f"\nError args: {error.args}"
  message += f"\nError __cause__: {error.__cause__}"

  await ErrorMessage(bot, message)