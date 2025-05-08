from discord.ui import Select, View
import discord

async def SelectMenu(interaction:discord.Interaction,
                     message:str,
                     placeholder:str,
                     dynamic_options):
  allowed_options = dynamic_options[:25]
  
  select = Select(
    placeholder=placeholder,
    options=[
      discord.SelectOption(label=option[1].title(),value=option[0]) for option in allowed_options
    ])

  async def my_callback(interaction):
    await interaction.response.send_message('Thank you! Submitting now...', ephemeral=True)
    view.stop()

  select.callback = my_callback
  view = View()
  view.add_item(select)
  await interaction.followup.send(message, view=view, ephemeral=True)
  await view.wait()
  item = FindItem(select.values[0], allowed_options)
  return item

def FindItem(id, options):
  for option in options:
    if option[0] == int(id):
      return option