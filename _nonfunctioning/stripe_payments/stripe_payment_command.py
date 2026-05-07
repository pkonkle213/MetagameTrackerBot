import discord
import stripe
from discord.ext import commands
from discord import app_commands, Interaction
from services.command_error_service import Error
import settings

PAYMENT_CURRENCY = 'usd'

TIERS = {
  'player': {'amount': 500,  'label': '$5.00/month',  'name': 'Player Monthly Subscription'},
  'store':  {'amount': 1000, 'label': '$10.00/month', 'name': 'Store Monthly Subscription'},
  'hub':    {'amount': 2000, 'label': '$20.00/month', 'name': 'Hub Monthly Subscription'},
}


async def create_subscription_session(interaction: Interaction, tier: str) -> None:
  await interaction.response.defer(ephemeral=True)

  if not settings.STRIPE_SECRET_KEY:
    await interaction.followup.send(
      "Payments are not configured yet. Please contact the bot owner.",
      ephemeral=True
    )
    return

  stripe.api_key = settings.STRIPE_SECRET_KEY
  config = TIERS[tier]

  session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
      'price_data': {
        'currency': PAYMENT_CURRENCY,
        'unit_amount': config['amount'],
        'product_data': {
          'name': config['name'],
        },
        'recurring': {
          'interval': 'month',
        },
      },
      'quantity': 1,
    }],
    mode='subscription',
    success_url='https://discord.com/channels/@me',
    cancel_url='https://discord.com/channels/@me',
    metadata={
      'discord_user_id': str(interaction.user.id),
      'discord_user_name': str(interaction.user.name),
      'discord_guild_id': str(interaction.guild_id),
      'tier': tier,
    }
  )

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
    await create_subscription_session(interaction, 'player')

  @app_commands.command(name='store',
                        description='Subscribe as a Store for $10.00/month')
  @app_commands.guild_only()
  async def StorePayCommand(self, interaction: Interaction):
    await create_subscription_session(interaction, 'store')

  @app_commands.command(name='hub',
                        description='Subscribe as a Hub for $20.00/month')
  @app_commands.guild_only()
  async def HubPayCommand(self, interaction: Interaction):
    await create_subscription_session(interaction, 'hub')

  @PlayerPayCommand.error
  @StorePayCommand.error
  @HubPayCommand.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)


async def setup(bot):
  await bot.add_cog(StripePaymentCommands(bot))
