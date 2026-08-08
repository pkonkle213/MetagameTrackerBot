import discord
from tuple_conversions import PlayerArchetype

class MassArchetypeSubmit(discord.ui.Modal, title='Submit Archetypes'):
  def __init__(self, players:list[PlayerArchetype]):
    super().__init__()
    self.interaction: discord.Interaction | None = None
    self.players = players
    self.new_archetypes: list[PlayerArchetype] = []
    self.is_submitted = False
    
    num_players = len(players)

    for i in range(0, len(players)):
      self.add_item(
        discord.ui.Label(
          text=f'{players[i].player_name}',
          component=discord.ui.TextInput(
            custom_id=str(i),
            placeholder=f"{players[i].player_name}'s archetype",
            default=players[i].archetype_played,
            style=discord.TextStyle.short,
            required=True,
            max_length=100,
            min_length=2
          )
        )
      )

  async def on_submit(self, interaction: discord.Interaction):
    for i in range(0, len(self.players)):
      name = self.players[i].player_name
      archetype = self.children[i].component.value.title()
      self.new_archetypes.append(PlayerArchetype(name, archetype))

    self.new_interaction = interaction
    await interaction.response.defer(ephemeral=True)
    self.is_submitted = True
    