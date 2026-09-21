from discord import ButtonStyle, Interaction, ui
from tuple_conversions import ViewButtonEnum


class ConfirmData(ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.action = None
        self.interaction: Interaction | None = None

    @ui.button(label="Cancel", style=ButtonStyle.danger)
    async def cancel(self, interaction: Interaction, button: ui.Button):
        self.action = ViewButtonEnum.Cancel.value
        self.interaction = interaction
        self.stop()

    @ui.button(label="Continue", style=ButtonStyle.primary)
    async def approve_event(self, interaction: Interaction, button: ui.Button):
        self.action = ViewButtonEnum.Continue.value
        self.interaction = interaction
        self.stop()

    @ui.button(label="Done, Event Complete", style=ButtonStyle.success)
    async def mark_complete(self, interaction: Interaction, button: ui.Button):
        self.action = ViewButtonEnum.DoneComplete.value
        self.interaction = interaction
        self.stop()

    @ui.button(label="Done, Event Incomplete", style=ButtonStyle.secondary)
    async def mark_incomplete(self, interaction: Interaction, button: ui.Button):
        self.action = ViewButtonEnum.DoneIncomplete.value
        self.interaction = interaction
        self.stop()
