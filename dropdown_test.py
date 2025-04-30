
#This is close, but the options aren't flexible.
#I'd like to present options accurate to the game that is being played
@client.tree.command(name="atest",
                     description="The new thing I want to test",
                     guild=settings.TESTSTOREGUILD)
async def ATest(interaction: discord.Interaction):
  options = [
      discord.SelectOption(label=game.Name, value=game.ID)
      for game in data_translation.GetAllGames()
  ]
  view = FormatDropdown(options)

  await interaction.response.send_message(view=view)
  await view.wait()

  print('Answer:', view.answer)
  await interaction.response.send_message(f'You chose {view.answer[0]}')

class FormatDropdown(discord.ui.View):

  def __init__(self, options):
    self.options = options

  answer = None

  @discord.ui.select(placeholder="Choose a format",
                     min_values=1,
                     max_values=1,
                     options=[
                         discord.SelectOption(label=game.Name, value=game.ID)
                         for game in data_translation.GetAllGames()
                     ])
  async def select_format(self, interaction: discord.Interaction,
                          select: discord.ui.Select):
    self.answer = select.values
    self.stop()