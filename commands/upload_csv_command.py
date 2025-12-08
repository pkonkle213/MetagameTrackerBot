import os
from datetime import datetime
from discord import app_commands, Interaction, Attachment
from discord.ext import commands
from services.object_storage_service import upload_bytes
from services.command_error_service import Error
from custom_errors import KnownError


class UploadCSVCommand(commands.Cog):
    """Commands for uploading CSV files to App Storage"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="upload_csv",
                          description="Upload a CSV file to the NewEventData storage bucket")
    @app_commands.guild_only()
    async def upload_csv(self, interaction: Interaction, csv_file: Attachment):
        """
        Parameters
        ----------
        csv_file: Attachment
            The CSV file to upload to storage
        """
        await interaction.response.defer(ephemeral=True)

        if not csv_file.filename.endswith('.csv'):
            raise KnownError("Please upload a file with a '.csv' extension.")

        try:
            file_content = await csv_file.read()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = os.path.splitext(csv_file.filename)[0]
            destination_name = f"{base_name}_{timestamp}.csv"
            
            storage_path = upload_bytes(file_content, destination_name, "text/csv")
            
            await interaction.followup.send(
                f"Successfully uploaded `{csv_file.filename}` to storage as `{destination_name}`\nStorage path: `{storage_path}`",
                ephemeral=True
            )
        except Exception as e:
            raise KnownError(f"Failed to upload file: {str(e)}")

    @upload_csv.error
    async def upload_csv_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        await Error(self.bot, interaction, error)


async def setup(bot):
    await bot.add_cog(UploadCSVCommand(bot))
