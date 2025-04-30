#Command name: report
#async def NaughtyWords(self, interaction: discord.Interaction, text: app_commands.Argument(str, min_length=3))

#1) Ensure length is at least 3. Test the app_commands limitation and this may be unnecessary
#2) add string to table of bad words (word should be unique, but call should be made)
#3) Update many-to-many relationship for the word and store
#4) update all archetypes within a 3 week timeframe that contain word '%WORD%' to 'UNKNOWN', returning affected rows
#5) update INPUTTRACKER table where word was used to 'REPORTED'
#6) send a message to the user that the word has been reported

#Side quests:
#inputtracker needs a new column for 'REPORTED' to ensure that some record is left as to why the entry was reported
#inputtracker needs a new column for 'player_id', foreign key related to participants.id. Obtain the id by changing the current UPDATE command to a SELECT
#Getting the archetype should link participants and events to inputtracker, using limit 1, order by date descending, and isn't disabled
#participants needs to lose 'archetype_played' column, inputtracker can probably lose the 'player_name' column as it will be linked by participants.id
#Metagame data will need to retrive the archetype_played from inputtracker, not participants. This is duplicate data and should be handled smarter