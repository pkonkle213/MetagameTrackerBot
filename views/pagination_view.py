from discord import ui, ButtonStyle, Interaction
from discord.embeds import Embed


class PaginationView(ui.View):
    def __init__(self, pages: list[Embed]):
        super().__init__(timeout=180)  # View times out in 3 minutes
        self.pages = pages
        self.current_page = 0

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

    async def update_page(self, interaction: Interaction):
        """Edits the message to display the current page's table and disables/enables buttons appropriately."""
        embed = self.pages[self.current_page]

        # Update the page footer to show current progress (e.g., Page 1 of 6)
        embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.pages)}")

        # Update button states
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1

        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="◄", style=ButtonStyle.primary, disabled=True)
    async def prev_button(self, interaction: Interaction, button: ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_page(interaction)

    @ui.button(label="►", style=ButtonStyle.primary, disabled=False)
    async def next_button(self, interaction: Interaction, button: ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_page(interaction)
