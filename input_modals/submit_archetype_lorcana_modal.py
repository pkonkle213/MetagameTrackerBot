from discord import Interaction, SelectOption, ui
from discord.ext import commands

from custom_errors import KnownError
from services.input_services import ConvertInput
from services.submit_archetype_service import SubmitArchetype
from tuple_conversions import Event, Format, Game, Hub, Store

LORCANA_INKS = [
    SelectOption(label="Amber", value="Amber"),
    SelectOption(label="Amethyst", value="Amethyst"),
    SelectOption(label="Emerald", value="Emerald"),
    SelectOption(label="Ruby", value="Ruby"),
    SelectOption(label="Sapphire", value="Sapphire"),
    SelectOption(label="Steel", value="Steel"),
]


class LorcanaSubmitArchetypeModal(ui.Modal, title="Submit Archetype"):
    def __init__(
        self,
        bot: commands.Bot,
        store: Store | None,
        hub: Hub | None,
        game: Game,
        format: Format,
        events: list[Event],
        player_name: str,
        prev_archetypes: list[str],
        is_submitter: bool = False,
    ):
        super().__init__()
        self.bot = bot
        self.store = store
        self.hub = hub
        self.game = game
        self.format = format
        self.is_submitter = is_submitter

        self.past_events: list[SelectOption] = []
        for i in range(len(events)):
            option = events[i]
            label = f"{option.event_date.strftime('%m/%d')} - {option.event_name}"
            value = str(option.id)
            if i == 0:
                self.past_events.append(
                    SelectOption(label=label, value=value, default=True)
                )
            else:
                self.past_events.append(SelectOption(label=label, value=value))

        self.event_select = ui.Label(
            text="Event", component=ui.Select(options=self.past_events, required=True)
        )
        self.add_item(self.event_select)

        self.player_name_input = ui.Label(
            text="Player Name",
            component=ui.TextInput(
                placeholder="Player name",
                default=player_name if len(player_name) > 0 else "",
                required=True,
            ),
        )
        self.add_item(self.player_name_input)

        self.inks = ui.Label(
            text="Deck Inks",
            component=ui.Select(
                placeholder="Choose up to two inks...",
                required=True,
                options=LORCANA_INKS,
                max_values=2,
                min_values=1,
            ),
        )
        self.add_item(self.inks)

        self.archetype_name = ui.Label(
            text="Archetype Name",
            component=ui.TextInput(
                placeholder="Enter The Archetype Name", required=False, min_length=3
            ),
        )
        self.add_item(self.archetype_name)

    async def on_submit(self, interaction: Interaction) -> None:
        archetype = BuildArchetype(
            self.inks.component.values, self.archetype_name.component.value
        )
        event = GetEvent(self.past_events, self.event_select.component.values[0])
        player_name = ConvertInput(self.player_name_input.component.value)
        await interaction.response.defer(thinking=False)
        await SubmitArchetype(
            self.bot,
            interaction,
            player_name,
            event,
            archetype,
            self.store,
            self.hub,
            self.game,
            self.format,
            None,
            self.is_submitter,
        )


def BuildArchetype(inks: list[str], archetype_name: str) -> str:
    archetype = " / ".join(inks)
    archetype += f" - {archetype_name}"
    return archetype


def GetEvent(past_events: list[Event], event_id: str) -> Event:
    for event in past_events:
        if event.id == int(event_id):
            return event
    raise KnownError("No event found?")
