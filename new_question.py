import discord
from discord.ext import commands
from discord.ui import View, Select

class MyView(View):
  def __init__(self, options):
    super().__init__()
    self.options = options

  @discord.ui.select()
  async def my_select_callback(self, interaction: discord.Interaction, select: Select):
    await interaction.response.send_message(f'You selected {select.values[0]}')

async def setup(bot):
  await bot.add_cog(MyCog(bot))

class MyCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.my_options = [
      discord.SelectOption(label="Option 1", value="1"),
      discord.SelectOption(label="Option 2", value="2"),
      discord.SelectOption(label="Option 3", value="3"),
    ]

  @commands.command()
  async def show_select(self, ctx):
    view = MyView(self.my_options)
    await ctx.send("Select an option:", view=view)