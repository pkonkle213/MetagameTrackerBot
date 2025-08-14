from discord.ext import commands

async def MissingRoleError(interaction, error):
  if isinstance(error, commands.MissingRole):
    await interaction.response.send_message('You do not have the required role to use this command.', ephemeral=True)
  else:
    await interaction.response.send_message('Catch this:', type(error), ephemeral=True)