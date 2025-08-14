import os
import discord
from dotenv.main import load_dotenv

load_dotenv()

DISCORDTOKEN = os.getenv('DISCORDTOKEN')

DATAGUILDID = int(os.getenv('DATAGUILDID'))

APPROVALCHANNELID = int(os.getenv('BOTAPPROVALCHANNELID'))
ERRORCHANNELID = int(os.getenv('BOTERRORCHANNELID'))
CLAIMCHANNEL = int(os.getenv('CLAIMCHANNELID'))
BOTEVENTINPUTID = int(os.getenv('BOTEVENTINPUTID'))
FIVE6STOREID = int(os.getenv('FIVE6STOREID'))

MYBOTURL = os.getenv('MYBOTURL')
SOPURL = os.getenv('SOPURL')
FEEDBACKURL = os.getenv('FEEDBACKURL')
MYBOTGUILDURL = os.getenv('MYBOTGUILDURL')
DATAHUBINVITE = os.getenv('DATAHUBINVITE')

PHILID = int(os.getenv('PHILID'))

BOTGUILD = discord.Object(id=int(os.getenv('BOTGUILDID')))
TESTSTOREGUILD = discord.Object(id=int(os.getenv('TESTGUILDID')))