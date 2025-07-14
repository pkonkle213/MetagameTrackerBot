import os
import discord
from dotenv.main import load_dotenv

load_dotenv()

APPROVALCHANNELID = int(os.getenv('BOTAPPROVALCHANNELID'))
DISCORDTOKEN = os.getenv('DISCORDTOKEN')
ERRORCHANNELID = int(os.getenv('BOTERRORCHANNELID'))
MYBOTURL = os.getenv('MYBOTURL')
PHILID = int(os.getenv('PHILID'))
SOPURL = os.getenv('SOPURL')
FEEDBACKURL = os.getenv('FEEDBACKURL')
MYBOTGUILDURL = os.getenv('MYBOTGUILDURL')
DATAHUBINVITE = os.getenv('DATAHUBINVITE')
BOTEVENTINPUTID = int(os.getenv('BOTEVENTINPUTID'))
BOTGUILD = discord.Object(id=int(os.getenv('BOTGUILDID')))
DATAGUILDID = id=int(os.getenv('DATAGUILDID'))
TESTSTOREGUILD = discord.Object(id=int(os.getenv('TESTGUILDID')))
CLAIMCHANNEL = int(os.getenv('CLAIMCHANNELID'))
