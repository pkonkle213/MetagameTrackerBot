import discord
import stripe
from discord.ext import commands
from discord import app_commands, Interaction
from services.command_error_service import Error
import settings

PAYMENT_AMOUNT_CENTS = 500
PAYMENT_CURRENCY = 'usd'
PAYMENT_DESCRIPTION = '$5.00 Payment'


class StripePaymentCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='pay',
                        description='Generate a secure $5.00 payment link')
  @app_commands.guild_only()
  async def PayCommand(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)

    if not settings.STRIPE_SECRET_KEY:
      await interaction.followup.send(
        "Payments are not configured yet. Please contact the bot owner.",
        ephemeral=True
      )
      return

    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
      payment_method_types=['card'],
      line_items=[{
        'price_data': {
          'currency': PAYMENT_CURRENCY,
          'unit_amount': PAYMENT_AMOUNT_CENTS,
          'product_data': {
            'name': PAYMENT_DESCRIPTION,
          },
        },
        'quantity': 1,
      }],
      mode='payment',
      success_url='https://discord.com/channels/@me',
      cancel_url='https://discord.com/channels/@me',
      metadata={
        'discord_user_id': str(interaction.user.id),
        'discord_user_name': str(interaction.user.name),
        'discord_guild_id': str(interaction.guild_id),
      }
    )

    view = discord.ui.View()
    view.add_item(discord.ui.Button(
      label='Pay $5.00',
      url=session.url,
      style=discord.ButtonStyle.link,
      emoji='💳'
    ))

    await interaction.followup.send(
      f"Click the button below to securely complete your $5.00 payment.\n"
      f"-# This link expires in 24 hours and is for your use only.",
      view=view,
      ephemeral=True
    )

  @PayCommand.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)


async def setup(bot):
  await bot.add_cog(StripePaymentCommands(bot))
