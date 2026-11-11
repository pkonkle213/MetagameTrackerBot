from discord.ext import commands
from discord import ButtonStyle, Interaction, Object, app_commands, ui
from checks import isPhil
from data.database_commands_data import DatabaseCommandsDownload
from data.recent_event_copy_data import (
    COPY_WINDOW_WEEKS,
    CopyRecentEventsToStore,
    PreviewRecentEventCopy,
    RecentEventCopyPreview,
)
from settings import BOTGUILDID


class RecentEventCopyConfirmation(ui.View):
    def __init__(self, owner_id: int, preview: RecentEventCopyPreview):
        super().__init__(timeout=120)
        self.owner_id = owner_id
        self.preview = preview
        self.message = None
        self.finished = False

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "Only the command owner can confirm this copy.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        if self.message is not None:
            try:
                await self.message.edit(
                    content="Preview expired. No data was changed.", view=None
                )
            except Exception:
                pass

    @ui.button(label="Confirm copy", style=ButtonStyle.danger)
    async def confirm(
        self, interaction: Interaction, button: ui.Button
    ) -> None:
        if self.finished:
            await interaction.response.send_message(
                "This preview has already been used.", ephemeral=True
            )
            return
        self.finished = True
        self.stop()
        await interaction.response.edit_message(
            content="Copying the reviewed records…", view=None
        )
        try:
            result = await CopyRecentEventsToStore(self.preview)
        except Exception as error:
            print(
                "Recent event copy failed "
                f"({type(error).__name__}): {error}"
            )
            await interaction.followup.send(
                "The copy failed and the transaction was rolled back. "
                "No partial copy was committed.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"Copied {result.event_count} events, {result.pairing_count} pairings, "
            f"and {result.submission_count} archetype submissions.",
            ephemeral=True,
        )

    @ui.button(label="Cancel", style=ButtonStyle.secondary)
    async def cancel(
        self, interaction: Interaction, button: ui.Button
    ) -> None:
        self.finished = True
        self.stop()
        await interaction.response.edit_message(
            content="Copy cancelled. No data was changed.", view=None
        )


class DatabaseCommands(commands.GroupCog, name="database"):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name="download", description="Download the database")
    @app_commands.check(isPhil)
    async def DownloadDatabase(self, interaction: Interaction):
        await interaction.response.send_message(
            "Generating database export archives, please wait...", ephemeral=True
        )
        try:
            with await DatabaseCommandsDownload() as export:
                total_parts = len(export.files)
                for start in range(0, total_parts, 10):
                    files = export.files[start : start + 10]
                    first_part = start + 1
                    last_part = start + len(files)
                    await interaction.followup.send(
                        content=(
                            f"Database export archives "
                            f"{first_part}-{last_part} of {total_parts}."
                        ),
                        files=files,
                        ephemeral=True,
                    )
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

    @app_commands.command(
        name="copy_recent_events",
        description="Copy recent events and their pairings to a store",
    )
    @app_commands.describe(
        target_discord_id="Exact Discord ID of the destination store"
    )
    @app_commands.check(isPhil)
    async def CopyRecentEvents(
        self, interaction: Interaction, target_discord_id: str
    ):
        if (
            not target_discord_id.isdigit()
            or len(target_discord_id) > 19
            or int(target_discord_id) <= 0
        ):
            await interaction.response.send_message(
                "Enter a valid numeric Discord ID.", ephemeral=True
            )
            return

        target_id = int(target_discord_id)
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            preview = await PreviewRecentEventCopy(target_id)
        except Exception as error:
            print(
                "Recent event copy preview failed "
                f"({type(error).__name__}): {error}"
            )
            await interaction.edit_original_response(
                content="I couldn't prepare the preview. No data was changed."
            )
            return

        if not preview.target_is_registered or not preview.target_is_store:
            await interaction.edit_original_response(
                content="That Discord ID must exist in both the discords and stores tables."
            )
            return
        if preview.existing_target_event_count:
            await interaction.edit_original_response(
                content=(
                    "The destination already has events in the last 12 weeks. "
                    "I won't risk creating a second copy."
                )
            )
            return
        if not preview.event_count:
            await interaction.edit_original_response(
                content="No events were found in the last 12 weeks."
            )
            return

        view = RecentEventCopyConfirmation(
            owner_id=interaction.user.id,
            preview=preview,
        )
        await interaction.edit_original_response(
            content=self._copy_preview_message(preview),
            view=view,
        )
        view.message = await interaction.original_response()

    @staticmethod
    def _copy_preview_message(preview: RecentEventCopyPreview) -> str:
        destination = preview.target_store_name or "Unnamed store"
        date_range = (
            f"{preview.first_event_date} through {preview.last_event_date}"
            if preview.first_event_date and preview.last_event_date
            else f"the last {COPY_WINDOW_WEEKS} weeks"
        )
        return (
            f"Copy **{preview.event_count} events**, "
            f"**{preview.pairing_count} pairings**, and "
            f"**{preview.submission_count} archetype submissions** "
            f"({date_range}) to **{destination}** "
            f"(`{preview.target_discord_id}`)?\n"
            "This adds new rows; it does not copy decks or standings."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(DatabaseCommands(bot), guilds=[Object(id=BOTGUILDID)])
