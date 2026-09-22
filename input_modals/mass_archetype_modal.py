import discord
from tuple_conversions import PlayerArchetype


class MassArchetypeSubmit(discord.ui.Modal, title="Submit Archetypes"):
    def __init__(self, players: list[PlayerArchetype]):
        super().__init__()
        self.interaction: discord.Interaction | None = None
        self.players = players
        self.new_archetypes: list[PlayerArchetype] = []
        self.is_submitted = False

        num_players = len(players)

        for i in range(0, len(players)):
            self.add_item(
                discord.ui.Label(
                    text=f"{players[i].player_name}",
                    component=discord.ui.TextInput(
                        custom_id=str(i),
                        placeholder=f"{players[i].player_name}'s archetype",
                        default=players[i].archetype_played,
                        style=discord.TextStyle.short,
                        required=False,
                        max_length=100,
                    ),
                )
            )

    async def on_submit(self, interaction: discord.Interaction):
        for i in range(0, len(self.players)):
            name = self.players[i].player_name
            old_archetype = self.players[i].archetype_played
            new_archetype = self.children[i].component.value
            print("--Player Name--\n", name)
            print("--Old archetype--\n", f"|{old_archetype}|")
            print("--Archetype--\n", f"|{new_archetype}|")
            if old_archetype.title() != new_archetype.title():
                self.new_archetypes.append(PlayerArchetype(name, new_archetype.title()))

        print("--Player archetypes--\n", self.new_archetypes)
        self.new_interaction = interaction
        await interaction.response.defer(ephemeral=True)
        self.is_submitted = True
