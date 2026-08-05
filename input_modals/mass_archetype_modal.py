import discord
from tuple_conversions import PlayerArchetype

class MassArchetypeSubmit(discord.ui.Modal, title='Submit Archetypes'):
  def __init__(self, players:list[PlayerArchetype]):
    super().__init__()
    self.interaction: discord.Interaction | None = None
    self.players = players
    
    num_players = len(players)

    print('----Players received:----\n', players)
    print('----Number of players:----\n', num_players)

    for i in range(0, len(players)):
      self.add_item(
        discord.ui.Label(
          text=f'{players[i].player_name}',
          component=discord.ui.TextInput(
            custom_id=str(i),
            placeholder=f'Current archetype: {players[i].archetype_played}',
            style=discord.TextStyle.short,
            required=True,
            max_length=100,
            min_length=10
          )
        )
      )

  async def on_submit(self, interaction: discord.Interaction):
    self.new_interaction = interaction
    