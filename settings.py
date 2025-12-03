import os
from dotenv import load_dotenv

load_dotenv()

DISCORDTOKEN = os.environ['DISCORD_TOKEN']

BOTGUILDID = int(os.environ['BOT_GUILD_ID'])
TESTGUILDID = int(os.environ['TEST_GUILD_ID'])
DATAGUILDID = int(os.environ['DATA_GUILD_ID'])
FIVE6STOREID = int(os.environ['FIVE6_GUILD_ID'])

ERRORCHANNELID = int(os.environ['BOT_ERROR_ID'])
CLAIMCHANNEL = int(os.environ['BOT_CLAIMSTREAM_ID'])
BOTEVENTINPUTID = int(os.environ['BOT_NEWEVENT_ID'])

MYBOTURL = os.environ['BOT_URL_INSTALL']
SOPURL = os.environ['BOT_URL_SOP']
FEEDBACKURL = os.environ['BOT_URL_FEEDBACK']
MYBOTGUILDURL = os.environ['BOT_URL_GUILDINVITE']
DATAHUBINVITE = os.environ['DATAHUB_URL_INVITE']

PHILID = int(os.environ['PHIL_USERID'])