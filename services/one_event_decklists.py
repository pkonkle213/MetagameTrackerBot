from custom_errors import KnownError
from tuple_conversions import Event
import discord
from discord import app_commands
from discord.ext import commands
from data.event_decklists_data import GetDecks, GetDecklists

class DecklistPaginationView(discord.ui.View):
  def __init__(self, pages:list[discord.Embed]):
    super().__init__(timeout=180) # View times out in 3 minutes
    self.pages = pages
    self.current_page = 0

  async def on_timeout(self):
    for child in self.children:
      child.disabled = True

  async def update_page(self, interaction: discord.Interaction):
    """Edits the message to display the current page's table and disables/enables buttons appropriately."""
    embed = self.pages[self.current_page]

    # Update the page footer to show current progress (e.g., Page 1 of 6)
    embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.pages)}")

    # Update button states
    self.prev_button.disabled = self.current_page == 0
    self.next_button.disabled = self.current_page == len(self.pages) - 1

    await interaction.response.edit_message(embed=embed, view=self)

  @discord.ui.button(label="◄", style=discord.ButtonStyle.primary, disabled=True)
  async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    if self.current_page > 0:
      self.current_page -= 1
      await self.update_page(interaction)

  @discord.ui.button(label="►", style=discord.ButtonStyle.primary, disabled=False)
  async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    if self.current_page < len(self.pages) - 1:
      self.current_page += 1
      await self.update_page(interaction)
          
async def OneEventDecklists(interaction:discord.Interaction, event:Event) -> None:
  decklist_output = []
  # 1) Get all decks from the event
  decks = GetDecks(event)
  
  # 2) For all decks, make a list of ids
  
  # 3) Get all decklists for those decks
  decklists = GetDecklists(event)

  # 4) For each deck, create the title of '{archetype} ({wins} - {losses} - {draws})'
  # 5) For each deck, create a list of cards like:
  for deck in decks:
    title = f'{deck.archetype_played} ({deck.wins} - {deck.losses} - {deck.draws})'
    mainboard_list = [f'{card.quantity} {card.card_name}' for card in decklists if card.deck_id == deck.id and card.is_mainboard]
    mainboard = '\n'.join(mainboard_list)
    
    sideboard_list = [f'{card.quantity} {card.card_name}' for card in decklists if card.deck_id == deck.id and not card.is_mainboard]
    sideboard = '\n'.join(sideboard_list)

    description = f'Mainboard\n---------\n{mainboard}\n\nSideboard\n---------\n{sideboard}'
    embed = discord.Embed(title=title, description=description)
    
    # 6) Assign to a list of embeds, initialize view, and send
    decklist_output.append(embed)

  if len(decklist_output) < 1:
    raise KnownError('No decklists found for this event')

  
  view = DecklistPaginationView(decklist_output)
  initial_embed = decklist_output[0]
  initial_embed.set_footer(text=f"Page 1 of {len(decklist_output)}")
  await interaction.followup.send(embed=initial_embed, view=view, ephemeral=True)