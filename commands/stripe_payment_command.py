import discord
from discord import Interaction, app_commands
from discord.ext import commands

import settings
from services.command_error_service import Error
from services.stripe_payment_service import (
    PAYMENT_TIERS,
    create_subscription_session,
)


async def send_subscription_link(
    interaction: Interaction, tier: str, billing_period: str
) -> None:
    config = PAYMENT_TIERS.get(tier, {}).get(billing_period)
    if config is None:
        raise ValueError("Unknown subscription tier or billing period")

    if not settings.STRIPE_SECRET_KEY:
        await interaction.response.send_message(
            "Payments are not configured yet. Please contact the bot owner.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)
    session = await create_subscription_session(
        tier=tier,
        billing_period=billing_period,
        discord_user_id=interaction.user.id,
        discord_user_name=interaction.user.name,
        discord_guild_id=interaction.guild_id,
    )
    if not session.url:
        raise RuntimeError("Stripe did not return a Checkout URL")

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label=f'Subscribe {config["label"]}',
            url=session.url,
            style=discord.ButtonStyle.link,
            emoji="💳",
        )
    )

    await interaction.followup.send(
        f"Click the button below to start your **{config['name']}** at "
        f"**{config['label']}**.\n"
        "-# This link expires in 24 hours and is for your use only.",
        view=view,
        ephemeral=True,
    )


class StripePaymentCommands(commands.GroupCog, name="pay"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="player", description="Subscribe as a Player")
    @app_commands.guild_only()
    @app_commands.choices(
        billing_period=[
            app_commands.Choice(name="Monthly — $5", value="monthly"),
            app_commands.Choice(name="Yearly — $50", value="yearly"),
        ]
    )
    async def PlayerPayCommand(
        self,
        interaction: Interaction,
        billing_period: app_commands.Choice[str],
    ):
        await send_subscription_link(interaction, "player", billing_period.value)

    @app_commands.command(name="store", description="Subscribe as a Store")
    @app_commands.guild_only()
    @app_commands.choices(
        billing_period=[
            app_commands.Choice(name="Monthly — $10", value="monthly"),
            app_commands.Choice(name="Yearly — $100", value="yearly"),
        ]
    )
    async def StorePayCommand(
        self,
        interaction: Interaction,
        billing_period: app_commands.Choice[str],
    ):
        await send_subscription_link(interaction, "store", billing_period.value)

    @PlayerPayCommand.error
    @StorePayCommand.error
    async def Errors(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        await Error(self.bot, interaction, error)


async def setup(bot):
    await bot.add_cog(StripePaymentCommands(bot))
