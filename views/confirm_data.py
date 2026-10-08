from discord import ButtonStyle, Interaction, ui
from tuple_conversions import ViewButtonEnum


class ConfirmData(ui.View):
    def __init__(self, is_standings: bool = False, next_modal: ui.Modal | None = None):
        super().__init__(timeout=120)
        self.action = None
        self.interaction: Interaction | None = None
        self.next_modal = next_modal

        self.btn_cancel = ui.Button(
            label="Cancel",
            style=ButtonStyle.secondary
        )
        self.btn_continue = ui.Button(
            label="Continue",
            style=ButtonStyle.primary
        )
        self.btn_complete = ui.Button(
            label="Done and Complete",
            style=ButtonStyle.success
        )
        self.btn_incomplete = ui.Button(
            label="Done and Incomplete",
            style=ButtonStyle.danger
        )

        self.btn_cancel.callback = self.cancel_callback
        self.btn_continue.callback = self.continue_callback
        self.btn_complete.callback = self.complete_callback
        self.btn_incomplete.callback = self.incomplete_callback

        self.add_item(self.btn_cancel)

        if not is_standings:
            self.add_item(self.btn_continue)

        self.add_item(self.btn_complete)
        self.add_item(self.btn_incomplete)


   
    async def cancel_callback(self, interaction: Interaction):
        self.action = ViewButtonEnum.Cancel.value
        self.interaction = interaction
        self.stop()


    async def continue_callback(self, interaction: Interaction):
        self.action = ViewButtonEnum.Continue.value
        self.interaction = interaction
        if self.next_modal:
            await interaction.response.send_modal(self.next_modal)
        self.stop()

    
    async def complete_callback(self, interaction: Interaction):
        self.action = ViewButtonEnum.DoneComplete.value
        self.interaction = interaction
        await interaction.response.send_message(
            "Thank you for submitting data!", ephemeral=True
        )
        self.stop()

    
    async def incomplete_callback(self, interaction: Interaction):
        self.action = ViewButtonEnum.DoneIncomplete.value
        self.interaction = interaction
        await interaction.response.send_message(
            "Thank you for submitting data!", ephemeral=True
        )
        self.stop()
