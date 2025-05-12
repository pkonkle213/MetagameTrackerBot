import os
import discord
from dotenv.main import load_dotenv

load_dotenv()

APPROVALCHANNELID = int(os.getenv('BOTAPPROVALCHANNELID'))
BOTGUILD = discord.Object(id=int(os.getenv('BOTGUILDID')))
DISCORDTOKEN = os.getenv('DISCORDTOKEN')
ERRORCHANNELID = int(os.getenv('BOTERRORCHANNELID'))
MYBOTURL = os.getenv('MYBOTURL')
PHILID = int(os.getenv('PHILID'))
TESTSTOREGUILD = discord.Object(id=int(os.getenv('TESTGUILDID')))
SOPURL = os.getenv('SOPURL')
DATAGUILDID = id=int(os.getenv('DATAGUILDID'))
FEEDBACKURL = os.getenv('FEEDBACKURL')
MYBOTGUILDURL = os.getenv('MYBOTGUILDURL')