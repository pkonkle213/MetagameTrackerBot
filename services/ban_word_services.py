from interaction_objects import GetObjectsFromInteraction
from data.ban_word_data import AddWord, GetWord, MatchDisabledArchetypes, DisableMatchingWords, AddBadWordBridge, CheckStoreBannedWords, GetOffenders
from discord import Interaction

def AddBadWord(interaction:Interaction, bad_word:str):
  word = GetWord(bad_word)
  if word is None:
    word = AddWord(bad_word)
    if word is None:
      raise Exception('Unable to add word')  

  bridge_check = AddBadWordBridge(interaction.guild_id, word.ID)
  if bridge_check is None:
    raise Exception('Unable to add bad word bridge')
    
  archetypes = DisableMatchingWords(interaction.guild_id, bad_word.upper())
  if archetypes is None:
    raise Exception('No archetypes found to disable')
  return (word, archetypes)
  
def ContainsBadWord(discord_id:int, archetype:str):
  words = CheckStoreBannedWords(discord_id, archetype)
  return True if words else False

def CanSubmitArchetypes(discord_id:int, user_id:int):
  offenses = MatchDisabledArchetypes(discord_id, user_id)
  return len(offenses) < 3

def Offenders(interaction:Interaction):
  game, format, store, user_id = GetObjectsFromInteraction(interaction, game=True, store=True)
  offenders = GetOffenders(game, format, store)
  headers = ['Date Submitted', 'Submitter', 'Submitter ID', 'Event Date', 'Player Name', 'Archetype Played']
  if not format:
    headers.insert(5, 'Format')
  if not game:
    headers.insert(5, 'Game')
  title = 'Those who have been flagged for bad words/phrases'
  return offenders, title, headers