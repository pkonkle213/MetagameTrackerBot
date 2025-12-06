import discord

async def MessageUser(bot, msg, userId, files=None):
  user = await bot.fetch_user(userId)
  if files is None:
    await user.send(f'{msg}')
  else:
    await user.send(f'{msg}', files=files)

async def MessageChannel(bot, msg, guildId, channelId, file=None):
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

    if file is None:
      await channel.send(f'{msg}')
    else:
      await channel.send(f'{msg}', file=file)
    