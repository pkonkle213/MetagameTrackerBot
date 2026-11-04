import discord

from data.archetype_data import OpponentArchetype
from tuple_conversions import PlayerArchetype


class OpponentArchetypeModal(discord.ui.Modal, title="Opponent Archetypes"):
    def __init__(self, opponents: list[OpponentArchetype]):
        super().__init__()
        self.opponents = opponents
        self.interaction: discord.Interaction | None = None
        self.is_submitted = False
        self.new_archetypes: list[PlayerArchetype] = []

        for index, opponent in enumerate(opponents):
            label = f"Round {opponent.round_number} - {opponent.opponent_name}"
            if len(label) > 45:
                label = label[:42] + "..."
            self.add_item(
                discord.ui.Label(
                    text=label,
                    component=discord.ui.TextInput(
                        custom_id=str(index),
                        placeholder="Opponent archetype",
                        default=opponent.archetype_played or None,
                        style=discord.TextStyle.short,
                        required=False,
                        max_length=100,
                    ),
                )
            )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        for index, opponent in enumerate(self.opponents):
            archetype = self.children[index].component.value.strip()
            previous = (opponent.archetype_played or "").strip()
            if archetype and archetype.casefold() != previous.casefold():
                self.new_archetypes.append(
                    PlayerArchetype(opponent.opponent_name, archetype.title())
                )

        self.interaction = interaction
        await interaction.response.defer(ephemeral=True)
        self.is_submitted = True
