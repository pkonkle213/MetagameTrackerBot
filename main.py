from datetime import datetime as dt, time, timezone
import settings
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
from discord import Guild, Interaction, app_commands, Intents, NotFound, Forbidden
from discord.ext import commands, tasks
from settings import PHILID, DISCORDTOKEN
import timedposts.automated_paid_users as apu
from timedposts.automated_check_events import EventCheck
from timedposts.automated_updates import UpdateDataGuild
from services.store_services import NewStoreRegistration
from services.sync_service import SyncCommands
from discord_messages import MessageUser

intents = Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="?", intents=intents)

BASE_DIR = Path(__file__).parent
CMDS_DIR = BASE_DIR / "commands"
TIME_ZONE = timezone("US/Eastern")


@bot.event
async def on_ready():
    print(f"Logged on as {format(bot.user)}!")
    data_guild_update.start()
    find_the_unknown.start()
    sync_paid_users.start()
    await SyncCommands(bot, CMDS_DIR)
    print("Synced commands. Good to go")


@bot.event
async def on_guild_join(guild: Guild):
    """This event triggers when the bot joins a new guild (server)."""
    output = (
        "Thank you for adding me to your server! Here's my notes from installation:\n"
    )
    output += await NewStoreRegistration(bot, guild)
    if guild.owner:
        await guild.owner.send(output)
    success = apu.UpdateStores()
    if success:
        output += "- Stores check has been updated"
    else:
        output += "- Stores check has failed"
    await MessageUser(bot, f"New guild joined: {guild.name}\n{output}", PHILID)


@bot.event
async def on_app_command_completion(
    interaction: Interaction, command: app_commands.Command
):
    """Logs successfully executed slash commands using the interaction object."""
    # 2. Extract user and command details
    username = str(interaction.user)
    command_name = command.name
    group_names = []

    current_parent = command.parent
    while current_parent is not None:
        group_names.insert(0, current_parent.name)
        current_parent = current_parent.parent

    # Combine groups if they exist (e.g., "mod user" or "economy")
    full_group_name = " ".join(group_names) if group_names else "None"

    # Construct the full visual command string (e.g., "/mod user ban")
    full_command_path = f"/{' '.join(group_names)} {command_name}".replace(
        "  ", " "
    ).strip()

    # 3. Extract parameter values from the interaction's namespace
    # interaction.namespace holds the arguments passed by the user
    if interaction.namespace:
        # Converts the namespace arguments into a readable string
        params = ", ".join(f"{name}: {value}" for name, value in interaction.namespace)
    else:
        params = "None"

    # 4. Format the log message
    log_message = (
        f"```Slash Command Executed\n"
        f"User: {username} (ID: {interaction.user.id})\n"
        f"Command Group: {full_group_name}\n"
        f"Command Name: {command_name}\n"
        f"Full Invocation: {full_command_path}\n"
        f"Arguments: {params}\n"
        f"Guild: {interaction.guild.name}\n"
        f"Channel: {interaction.channel.id if interaction.channel else 'DM'}```"
    )

    # 1. Fetch the target channel
    channel = bot.get_channel(settings.BOTLOGCHANNEL)
    if channel is None:
        try:
            channel = await bot.fetch_channel(settings.BOTLOGCHANNEL)
        except (NotFound, Forbidden):
            print(f"Log channel not found or bot lacks permissions.\n{log_message}")
            return

    # 5. Send the log
    try:
        await channel.send(log_message)
    except Forbidden:
        print(
            f"Bot doesn't have permission to send messages in the log channel.\n{log_message}"
        )


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
        apu.UpdateStores()
        apu.UpdateHubs()
        apu.UpdatePaidUsers()
        apu.UpdatePaidStores()
        apu.UpdatePaidHubs()


@sync_paid_users.before_loop
async def before_sync_paid_users():
    await bot.wait_until_ready()


@tasks.loop(time=time(hour=10, minute=00, tzinfo=TIME_ZONE))
async def data_guild_update():
    """Every Friday at 10:00 AM EST, the data guild is updated with new data"""
    time_now = dt.now(timezone.utc)
    if time_now.weekday() == 4:  # Check if it's Friday, 0 = Monday
        try:
            await UpdateDataGuild(bot)
        except Exception as error:
            print(f"Error updating data guild: {error}")


@data_guild_update.before_loop
async def before_scheduled_post():
    await bot.wait_until_ready()


bot.run(DISCORDTOKEN)
