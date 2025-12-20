import discord
from discord.ext import commands
from typing import Optional, Sequence
from discord.file import File


#TODO: How do I type files??
async def MessageUser(bot: commands.Bot, msg:str, userId:int, files:Optional[Sequence[File]] = None):
  user = await bot.fetch_user(userId)
  if files:
    await user.send(f'{msg}', files=files)
  else:
    await user.send(f'{msg}')

async def MessageChannel(bot:commands.Bot, msg:str, guildId:int, channelId:int):
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
    