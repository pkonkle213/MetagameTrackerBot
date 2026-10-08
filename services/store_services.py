from numpy.char import join
from services.input_services import ConvertInput
from discord_messages import MessageUser
from discord import Interaction, Guild, utils, Permissions
from discord.ext import commands
from custom_errors import KnownError
from data.formats_data import AddFormatMap, GetFormatsByGameId
from data.games_data import AddGameMap
from data.store_data import (
    AddStore,
    UpdateStore,
    AddDiscord,
    UpdateHub,
    UpdateApprovedHubs,
)
from input_modals.store_profile_update import StoreProfileModal
from input_modals.hub_profile_update import HubProfileModal
from data.interaction_data import GetObjectsFromInteraction
from services.game_mapper_services import GetGameOptions
from settings import BOTGUILDID, PHILID
from tuple_conversions import Format, Game, MTBRoles


async def UpdateDetails(bot: commands.Bot, interaction: Interaction) -> Interaction:
    """Updates the store details in the database"""
    objects = await GetObjectsFromInteraction(interaction)
    if not objects.store and not objects.hub:
        raise KnownError("No registered discord found")

    if objects.store:
        modal = await StoreProfileModal.create(
            bot, objects.store, objects.game, objects.format
        )
        await interaction.response.send_modal(modal)
        await modal.wait()

    if not modal.is_submitted:
      raise KnownError('Modal not submitted correctly')
    
    result = await UpdateStore(
      interaction,
      objects.store,
      modal.submitted_store_name,
      modal.submitted_store_address,
      modal.submitted_melee_id,
      modal.submitted_melee_secret
    )
    hubs = await UpdateApprovedHubs(
      objects.store,
      objects.game,
      objects.format,
      modal.submitted_hubs)

    if objects.hub:
        modal = HubProfileModal(bot, objects.hub)
        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.is_submitted:
            raise KnownError("Modal not submitted correctly")

    result = await UpdateHub(
      interaction,
      objects.hub.discord_id,
      modal.submitted_hub_name,
      modal.submitted_hub_invite
    )
  
  if result:
    return modal.new_interaction
  else:
    raise KnownError('Profile unable to update')
  

async def NewStoreRegistration(bot: commands.Bot, guild: Guild) -> list[str]:
    """Goes through steps to register a new store and automap categories and channels"""
    output: list[str] = []
    # TODO: Define discord_name, owner_name, and owner_id and others here as they're used in multiple places
    try:
        print("Adding discord to database")
        add_discord = AddDiscordToDatabase(guild)
        if add_discord:
            output.append("- Discord added to database")

    print('Adding store to database')
    add_store = await AddStoreToDatabase(guild)
    if add_store:
      output += '- Store added to database\n'

        print("Mapping categories and channels")
        mapping_message, mapping_success = await MapCategoriesAndChannels(guild)
        if mapping_success:
            output.append("- Categories and channels automapped:")
            output += mapping_message
        else:
            output.append("- No categories or channels automapped")

        print("Creating and assigning MTStore role")
        output += await CreateRole(guild, MTBRoles.MTStore.name)

        print("Creating and assigning MTSubmitter role")
        output += await CreateRole(guild, MTBRoles.MTSubmitter.name)

        print("Assigning Store Owner role in bot guild")
        owner = guild.owner
        if owner is None:
            raise Exception("No owner found")
        role_assign = await AssignStoreOwnerRoleInBotGuild(bot, owner.id)
        return output
    except Exception as e:
        await MessageUser(bot, f"Issue with new store registration: {e}", PHILID)
        return [
            f"Unable to add this discord to my database. Please contact the bot owner."
        ]


async def AddDiscordToDatabase(guild: discord.Guild) -> str:
  """Adds the discord to the database"""
  guild_name = ConvertInput(guild.name)
  owner_name = ConvertInput(guild.owner.name) if guild.owner else 'Unknown'
  owner_id = guild.owner_id if guild.owner_id else 0
  await AddDiscord(guild.id, guild.name, owner_id, owner_name)
  return 'Done'

async def AddStoreToDatabase(guild: discord.Guild) -> int:
  """Adds the store to the database"""
  store = await AddStore(guild.id)
  return store


def MatchGame(category_name: str, games: list[Game]) -> Game | None:
    """Matches the category name to a game"""
    for game in games:
        if game.game_name.lower() in category_name.lower():
            return game


def MatchFormat(channel_name: str, formats: list[Format]) -> Format | None:
    """Matches the channel name to a format"""
    for format in formats:
        print(f"Checking {format.format_name.lower()} against {channel_name.lower()}")
        if format.format_name.lower() in channel_name.lower():
            return format


async def MapCategoriesAndChannels(guild: Guild) -> tuple[list[str], bool]:
    """Sequentially maps the categories and channels in the guild"""
    try:
        output: list[str] = []
        mapping = False
        games = await GetGameOptions()
        if games is None:
            raise Exception("No games found to automap")

        for category in guild.categories:
            game = MatchGame(category.name, games)
            if game:
                result = await AddGameMap(guild.id, game.id, category.id)
                mapping = True
                if result:
                    output.append(
                        f"Game: {game.game_name.title()}, Category: {category.name} ({category.id})"
                    )

                formats = await GetFormatsByGameId(game)
                if formats:
                    for channel in category.channels:
                        format = MatchFormat(channel.name, formats)
                        if format:
                            result = await AddFormatMap(guild.id, format.id, channel.id)
                            if result:
                                output.append(
                                    f"Format: {format.format_name.title()}, Channel: {channel.name} ({channel.id})"
                                )

        return output, mapping
    except Exception as e:
        print("Error received:", e)
        return "", False


async def CreateRole(guild: Guild, role_name: str) -> list[str]:
    """Creates the role and assigns it to the owner"""
    owner = guild.owner
    if owner is None:
        raise KnownError("No owner found")
    mtsubmitter_role = utils.get(guild.roles, name=role_name)

    output: list[str] = []
    success = ""
    if mtsubmitter_role is None:
        try:
            bot_member = guild.me
            print(
                f"Bot Global Permissions: {bot_member.guild_permissions.manage_roles}"
            )
            mtsubmitter_role = await guild.create_role(
                name=role_name,
                reason="Automatic role creation on join",
            )
            output.append(f"- {role_name} role created.")
            success = True
        except Exception as e:
            print("Ran into exception: ", e)
            output.append(
                f"- Unable to create {role_name} role. Please create and assign manually."
            )

    try:
        await owner.add_roles(mtsubmitter_role)
        output.append("- MTSubmitter role assigned to owner.")
        success = True
        return output
    except Exception as e:
        output.append(
            "- MTSubmitter role unable to be assigned to owner. Please assign manually."
        )
        return output


async def AssignStoreOwnerRoleInBotGuild(bot: commands.Bot, owner_id: int) -> str:
    """Assigns the Store Owner role to the owner in the bot guild"""
    bot_guild = bot.get_guild(BOTGUILDID)
    if bot_guild is None:
        return "Bot guild not found"
    user = await bot_guild.fetch_member(owner_id)

    if user is None:
        raise Exception("User not found")
    store_owner_role = utils.find(lambda r: r.name == "Store Owners", bot_guild.roles)
    if store_owner_role is None:
        raise Exception("Store Owner role not found")

    await user.add_roles(store_owner_role)
    return "If owner is in the bot's guild, they've been assigned the Store Owner role."
