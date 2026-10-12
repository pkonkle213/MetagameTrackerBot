from discord import Interaction, app_commands
from discord.ext import commands


class TestCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="test", description="testing")
    async def Test(self, interaction: Interaction):
        objects = interaction.extras.get("db_obj")
        print("Objects received:", objects)
        await interaction.followup.send("All done!")


async def setup(bot: commands.Bot):
    await bot.add_cog(TestCommand(bot))
