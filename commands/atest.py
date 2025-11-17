import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings
from timedposts.automated_check_events import GetEventsWithUnkown

TARGET_GUILDS = [settings.TESTGUILDID]
five6_id = settings.FIVE6STOREID
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  #@app_commands.checks.has_role('MTSubmitter')
  async def Testing(self,
                    interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    await TestThis(self.bot, interaction)
    await interaction.followup.send("Testing?")
  
  @Testing.error
  async def on_tree_error(self,
                          interaction: Interaction,
                          error: app_commands.AppCommandError):
    await interaction.response.send_message(str(error))

async def setup(bot):
  await bot.add_cog(ATest(bot))

async def TestThis(bot, interaction):
  guild = bot.get_guild(five6_id)

  if guild is None:
    raise Exception("Guild not found")

  channel = guild.get_channel(1210773681417224192)

  if channel is None:
    raise Exception("Channel not found")
  
  """
  permissions = channel.permissions_for(OBJ)

  print('General permissions:', permissions)
  """
  user_bot = guild.me
  if not user_bot:
    raise Exception("Bot not found")
  
  bot_permissions = channel.permissions_for(user_bot)
  print('Bot send_messages:', bot_permissions.send_messages)

  overwrite = discord.PermissionOverwrite()
  overwrite.send_messages = True

  try:
    await channel.set_permissions(user_bot, overwrite=overwrite)
    print('Maybe this gave the bot permissions?')
    bot_permissions = channel.permissions_for(user_bot)
    print('Bot send_messages:', bot_permissions.send_messages)
    
  except Exception as ex:
    print('Error setting permissions:', ex)