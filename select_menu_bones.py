from discord.ui import Select, View
import discord

#TODO: This needs to be adjusted, as my Lorcana menu needs to allow for two selections
async def SelectMenu(interaction:discord.Interaction,
                     message:str,
                     placeholder:str,
                     dynamic_options,
                     max_options = 1):
  allowed_options = dynamic_options[:25]
  print('Allowed options:',allowed_options)
  
  select = Select(
    placeholder=placeholder,
    options=[
      discord.SelectOption(label=option[1].title(),value=option[0]) for option in allowed_options
    ],
    min_values=1,
    max_values=max_options)

  async def my_callback(interaction):
    await interaction.response.send_message('Thank you! Submitting now...', ephemeral=True)
    view.stop()

  select.callback = my_callback
  view = View()
  view.add_item(select)
  await interaction.followup.send(message, view=view, ephemeral=True)
  await view.wait()
  print('Select:', select.values)
  items = FindItems(select.values,
                    allowed_options)
  return items

def FindItems(ids, options):
  items = []
  for id in ids:
    for option in options:
      if option[0] == int(id):
        items.append(option)
        
  return items