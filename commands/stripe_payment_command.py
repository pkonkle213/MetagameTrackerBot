import discord
from discord.ext import commands
from discord import app_commands, Interaction
from services.command_error_service import Error
from services.stripe_payment_service import (
  PAYMENT_TIERS,
  create_subscription_session,
)
import settings


async def send_subscription_link(
  interaction: Interaction, tier: str, billing_interval: str
) -> None:
  config = PAYMENT_TIERS.get(tier, {}).get(billing_interval)
  if config is None:
    raise ValueError("Unknown subscription tier or billing interval")

  if not settings.STRIPE_SECRET_KEY:
    await interaction.response.send_message(
      "Payments are not configured yet. Please contact the bot owner.",
      ephemeral=True,
    )
    return

  await interaction.response.defer(ephemeral=True)
  session = await create_subscription_session(
    tier=tier,
    billing_interval=billing_interval,
    discord_user_id=interaction.user.id,
    discord_user_name=interaction.user.name,
    discord_guild_id=interaction.guild_id,
  )
  if not session.url:
    raise RuntimeError("Stripe did not return a Checkout URL")

  view = discord.ui.View()
  view.add_item(discord.ui.Button(
    label=f'Subscribe {config["label"]}',
    url=session.url,
    style=discord.ButtonStyle.link,
    emoji='💳'
  ))

  await interaction.followup.send(
    f"Click the button below to start your **{config['name']}** at **{config['label']}**.\n"
    f"-# This link expires in 24 hours and is for your use only.",
    view=view,
    ephemeral=True
  )


class StripePaymentCommands(commands.GroupCog, name='pay'):
  def __init__(self, bot):
    self.bot = bot

  BILLING_INTERVAL_CHOICES = [
    app_commands.Choice(name='Monthly', value='monthly'),
    app_commands.Choice(name='Yearly', value='yearly'),
  ]

  @app_commands.command(name='player',
                        description='Subscribe as a Player with monthly or yearly billing')
  @app_commands.choices(billing_interval=BILLING_INTERVAL_CHOICES)
  @app_commands.guild_only()
  async def PlayerPayCommand(
    self,
    interaction: Interaction,
    billing_interval: app_commands.Choice[str],
  ):
    await send_subscription_link(interaction, 'player', billing_interval.value)

  @app_commands.command(name='store',
                        description='Subscribe as a Store with monthly or yearly billing')
  @app_commands.choices(billing_interval=BILLING_INTERVAL_CHOICES)
  @app_commands.guild_only()
  async def StorePayCommand(
    self,
    interaction: Interaction,
    billing_interval: app_commands.Choice[str],
  ):
    await send_subscription_link(interaction, 'store', billing_interval.value)

  @PlayerPayCommand.error
  @StorePayCommand.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)


async def setup(bot):
  await bot.add_cog(StripePaymentCommands(bot))
