import discord

#This was interesting, but I don't know how to utilize it yet
async def embed(interaction: discord.Interaction):
  embed = discord.Embed(title="Example Embed", description="This is an example embed.", color=0x00ff00)
  embed.add_field(name="Field 1", value="Value 1", inline=False)
  embed.add_field(name="Field 2", value="Value 2", inline=False)
  await interaction.response.send_message(embed=embed)
