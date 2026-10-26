from os import environ

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = environ["DATABASE_URL"]

DISCORDTOKEN = environ["DISCORD_TOKEN"]

BOTGUILDID = int(environ["BOT_GUILD_ID"])
DATAGUILDID = int(environ["DATA_GUILD_ID"])
FIVE6STOREID = int(environ["FIVE6_GUILD_ID"])

ERRORCHANNELID = int(environ["BOT_ERROR_ID"])
CLAIMCHANNEL = int(environ["BOT_CLAIMSTREAM_ID"])
BOTLOGCHANNEL = int(environ["BOT_LOG_CHANNELID"])

MYBOTURL = environ["BOT_URL_INSTALL"]
SOPURL = environ["BOT_URL_SOP"]
FEEDBACKURL = environ["BOT_URL_FEEDBACK"]

PHILID = int(environ["PHIL_USERID"])

STRIPE_SECRET_KEY = environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = environ.get("STRIPE_WEBHOOK_SECRET", "")
HTTP_SERVER_PORT = 8080
