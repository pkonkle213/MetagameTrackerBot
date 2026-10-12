from datetime import datetime as dt, time, timezone as datetime_timezone
from threading import Thread
from contextlib import suppress
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        self.send_error(404)

    def log_message(self, format, *args):
        pass


def StartHealthCheckServer():
    port = 8080
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthCheckHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    print(f"Health check server listening on port {port}", flush=True)


StartHealthCheckServer()

from pytz import timezone
from discord import (
    Guild,
    Interaction,
    Member,
    app_commands,
    Intents,
    NotFound,
    Forbidden,
)
from discord.ext import commands, tasks
from settings import PHILID, DISCORDTOKEN, BOTLOGCHANNEL
import timedposts.automated_paid_users as apu
from timedposts.automated_check_events import EventCheck
from timedposts.automated_updates import UpdateDataGuild
from services.store_services import NewStoreRegistration
from services.sync_service import SyncCommands
from checks import isMTStore, isMTSubmitter
from discord_messages import MessageUser
from data.interaction_data import GetObjectsFromInteraction
from data.command_invocations_data import (
    EnsureCommandInvocationsTable,
    LogCommandInvocation,
)
from tuple_conversions import InteractionObjects


async def get_interaction_objects(interaction: Interaction) -> InteractionObjects:
    return await GetObjectsFromInteraction(interaction)


class DatabaseCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: Interaction) -> bool:
        # Ping your DB every time a slash command is invoked
        db_data = await get_interaction_objects(interaction)

        # Attach the resulting object directly to the interaction object
        interaction.extras["db_object"] = db_data

        command = interaction.command
        if isinstance(command, app_commands.Command):
            member = interaction.user
            guild = interaction.guild
            has_mt_submitter_role = (
                isinstance(member, Member)
                and guild is not None
                and isMTSubmitter(guild, member)
            )
            has_mt_store_role = (
                isinstance(member, Member)
                and guild is not None
                and isMTStore(guild, member)
            )
            await LogCommandInvocation(
                user_id=interaction.user.id,
                command_name=f"/{command.qualified_name}",
                guild_id=interaction.guild_id,
                category_id=getattr(interaction.channel, "category_id", None),
                channel_id=interaction.channel_id,
                has_mt_submitter_role=has_mt_submitter_role,
                has_mt_store_role=has_mt_store_role,
            )

        # Return True to allow command execution to proceed
        return True


intents = Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="?", intents=intents, tree_cls=DatabaseCommandTree)

BASE_DIR = Path(__file__).parent
CMDS_DIR = BASE_DIR / "commands"
TIME_ZONE = timezone("US/Eastern")


@bot.event
async def on_ready():
    print(f"Logged on as {format(bot.user)}!")
    await EnsureCommandInvocationsTable()
    await apu.InitializePaidData()
    data_guild_update.start()
    find_the_unknown.start()
    sync_paid_users.start()
    await SyncCommands(bot, CMDS_DIR)
    print("Synced commands. Good to go")


@bot.event
async def on_guild_join(guild: Guild):
    """This event triggers when the bot joins a new guild (server)."""
    output = [
        "Thank you for adding me to your server! Here's my notes from installation:"
    ]
    output += await NewStoreRegistration(bot, guild)
    if guild.owner:
        await guild.owner.send("\n".join(output))
    success = await apu.UpdateStores()
    if success:
        output.append("- Stores check has been updated")
    else:
        output.append("- Stores check has failed")
    output.insert(0, f"New guild joined: {guild.name}")
    await MessageUser(bot, "\n".join(output), PHILID)


@tasks.loop(time=time(hour=18, minute=00, tzinfo=TIME_ZONE))
async def find_the_unknown():
    """Every day at 6:00 PM EST, the bot will check for events that are 3 days old and have unknown archetypes."""
    await EventCheck(bot)


@find_the_unknown.before_loop
async def before_find_the_unknown():
    await bot.wait_until_ready()


@tasks.loop(minutes=60)
async def sync_paid_users():
    """Every 60 minutes, the bot will sync the paid entities for command permission"""
    with suppress(Exception):
        await apu.UpdateStores()
        await apu.UpdateHubs()
        await apu.UpdatePaidUsers()
        await apu.UpdatePaidStores()
        await apu.UpdatePaidHubs()


@sync_paid_users.before_loop
async def before_sync_paid_users():
    await bot.wait_until_ready()


@tasks.loop(time=time(hour=10, minute=00, tzinfo=TIME_ZONE))
async def data_guild_update():
    """Every Friday at 10:00 AM EST, the data guild is updated with new data"""
    time_now = dt.now(datetime_timezone.utc)
    if time_now.weekday() == 4:  # Check if it's Friday, 0 = Monday
        try:
            await UpdateDataGuild(bot)
        except Exception as error:
            print(f"Error updating data guild: {error}")


@data_guild_update.before_loop
async def before_scheduled_post():
    await bot.wait_until_ready()


bot.run(DISCORDTOKEN)
