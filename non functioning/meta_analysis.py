#Need to update this for games that don't have formats yet
@bot.tree.command(name="metashift",
                     description="Provides a look at the metagame shift",
                     guild=settings.TESTSTOREGUILD)
async def MetagameShift(interaction: discord.Interaction,
                        weeks: int = 4):
  """
  Parameters
  ----------
  weeks: int
    Number of weeks in each range
  """
  await interaction.response.defer()
  output = data_translation.GetAnalysis(interaction, weeks)
  await interaction.followup.send(output)

@MetagameShift.error
async def MetagameShift_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

def GetAnalysis(interaction, weeks):
  data = interaction_data.GetInteractionData(interaction)

  #Uncomment to fake data
  #Comment to use true data
  discord_id = settings.TESTSTOREGUILD.id
  game = tuple_conversions.ConvertToGame((1, "Magic", True))
  format = tuple_conversions.ConvertToFormat((1, "Pauper"))

  dates = date_functions.GetAnalysisDates(weeks)
  data = database_connection.GetAnalysis(discord_id, game.ID, format.ID, weeks,
                                         True, dates)
  #If the True/False values flex the sql, it needs to flex the title and headers as well
  title = f'Percentage Shifts in Meta from {dates[3]} to {dates[0]}'
  headers = ['Archetype',
             'First Half Meta %',
             'Second Half Meta %',
             'Meta % Shift']
  output = output_builder.BuildTableOutput(title, headers, data)
  return output