#Not sure where I ripped this from, I possibly don't need it
def InteractionData(interaction):
  discord_id = interaction.guild.id
  game_name = interaction.channel.category.name
  game = GetGame(discord_id, game_name)
  if game.HasFormats:
    format_name = interaction.channel.name
    format = GetFormat(discord_id, game, format_name)
  else:
    format = None

  return tuple_conversions.InteractionDetails(game, format,
                                              interaction.guild.id,
                                              interaction.channel.id,
                                              interaction.user.id)

def GetAllGames():
  games_list = database_connection.GetAllGames()
  games = []
  for game in games_list:
    games.append(tuple_conversions.ConvertToGame(game))

  return games