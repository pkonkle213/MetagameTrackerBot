import discord
from discord.ext import commands
from discord import app_commands, Interaction
from services.command_error_service import Error
from services.stripe_payment_service import (
  PAYMENT_TIERS,
  create_subscription_session,
)
import settings


async def send_subscription_link(interaction: Interaction, tier: str) -> None:
  config = PAYMENT_TIERS.get(tier)
  if config is None:
    raise ValueError("Unknown subscription tier")

  if not settings.STRIPE_SECRET_KEY:
    await interaction.response.send_message(
      "Payments are not configured yet. Please contact the bot owner.",
      ephemeral=True,
    )
    return

  await interaction.response.defer(ephemeral=True)
  session = await create_subscription_session(
    tier=tier,
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

  @app_commands.command(name='player',
                        description='Subscribe as a Player for $5.00/month')
  @app_commands.guild_only()
  async def PlayerPayCommand(self, interaction: Interaction):
    await send_subscription_link(interaction, 'player')

  @app_commands.command(name='store',
                        description='Subscribe as a Store for $10.00/month')
  @app_commands.guild_only()
  async def StorePayCommand(self, interaction: Interaction):
    await send_subscription_link(interaction, 'store')

  @app_commands.command(name='hub',
                        description='Subscribe as a Hub for $20.00/month')
  @app_commands.guild_only()
  async def HubPayCommand(self, interaction: Interaction):
    await send_subscription_link(interaction, 'hub')

  @PlayerPayCommand.error
  @StorePayCommand.error
  @HubPayCommand.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)


async def setup(bot):
  await bot.add_cog(StripePaymentCommands(bot))
