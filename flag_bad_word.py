from collections import namedtuple
from database_connection import AddWord, GetWord, MatchDisabledArchetypes, DisableMatchingWords, AddBadWordBridge, GetWordsForDiscord
from discord import Interaction

def AddBadWord(interaction:Interaction, bad_word):
  #Check to see if word is in badwords
  Word = namedtuple("Word", ["ID", "word"])
  word_obj = GetWord(bad_word.upper())
  if word_obj is None or len(word_obj) == 0:
    #If not, add it
    word_obj = AddWord(bad_word.upper())
    if word_obj is None:
      raise Exception('Unable to add word')
  word = Word(word_obj[0][0], word_obj[0][1])

  #Add wordid and discordid to badword_store bridge table
  bridge_check = AddBadWordBridge(interaction.guild_id, word.ID)
  if bridge_check is None:
    raise Exception('Unable to add bad word bridge')
    
  #Disable all archetypes that contain the word
  archetypes = DisableMatchingWords(interaction.guild_id, bad_word.upper())
  if archetypes is None:
    raise Exception('No archetypes found to disable')
  return (word, archetypes)
  
def ContainsBadWord(interaction:Interaction, bad_word):
  bad_words = GetWordsForDiscord(interaction.guild_id)
  print('Bad words:', bad_words)
  for word in bad_words:
    print('Word:', word)
    if word[0] in bad_word.upper():
      print('We got one!')
      return True

  return False

def CanSubmitArchetypes(discord_id, user_id):
  offenses = MatchDisabledArchetypes(discord_id, user_id)
  return len(offenses) < 3