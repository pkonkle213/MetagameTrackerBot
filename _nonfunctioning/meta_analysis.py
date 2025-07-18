#Need to update this for games that don't have formats yet
@bot.tree.command(name="metashift",
                     description="Provides a look at the metagame shift",
                     guild=settings.TESTSTOREGUILD)
async def MetagameShift(interaction: discord.Interaction,
                        weeks: int = 4):
  """
  Parameters
  ----------
  weeks: int
    Number of weeks in each range
  """
  await interaction.response.defer()
  output = data_translation.GetAnalysis(interaction, weeks)
  await interaction.followup.send(output)

@MetagameShift.error
async def MetagameShift_error(interaction: discord.Interaction, error):
  await Error(interaction, error)

def GetAnalysis(interaction, weeks):
  data = interaction_data.GetInteractionData(interaction)

  #Uncomment to fake data
  #Comment to use true data
  discord_id = settings.TESTSTOREGUILD.id
  game = tuple_conversions.ConvertToGame((1, "Magic", True))
  format = tuple_conversions.ConvertToFormat((1, "Pauper"))

  dates = date_functions.GetAnalysisDates(weeks)
  data = database_connection.GetAnalysis(discord_id, game.ID, format.ID, weeks,
                                         True, dates)
  #If the True/False values flex the sql, it needs to flex the title and headers as well
  title = f'Percentage Shifts in Meta from {dates[3]} to {dates[0]}'
  headers = ['Archetype',
             'First Half Meta %',
             'Second Half Meta %',
             'Meta % Shift']
  output = output_builder.BuildTableOutput(title, headers, data)
  return output

def GetAnalysis(discord_id, game_id, format_id, weeks, isMeta, dates):
  (EREnd, ERStart, BREnd, BRStart) = dates
  formula = 'COUNT(*) * 1.0 / SUM(COUNT(*)) OVER()' if isMeta else '(sum(p.wins) * 1.0) / (sum(p.wins) + sum(p.losses))'
  with conn, conn.cursor() as cur:
    command = f"""
      SELECT archetype_played,
        ROUND(BeginningRange * 100, 2) AS BeginningRange,
        ROUND(EndingRange * 100, 2) AS EndingRange,
        ROUND((EndingRange - BeginningRange) * 100, 2) AS Shift
      FROM (
        SELECT Decks.archetype_played,
          SUM(COALESCE(BeginningRange.StatBR, 0)) AS BeginningRange,
          SUM(COALESCE(EndingRange.StatER, 0)) AS EndingRange
        FROM (
          SELECT DISTINCT archetype_played
          FROM participants
          WHERE event_id IN (
            SELECT id
            FROM events
            WHERE game_id = {game_id}
            AND format_id = {format_id}
            AND discord_id = {discord_id}
            AND event_date >= '{BRStart}'
            AND event_date <= '{EREnd}'
          )
        ) AS Decks
        LEFT OUTER JOIN (
          SELECT p.archetype_played,
            {formula} AS StatBR
          FROM participants p
          INNER JOIN events e ON p.event_id = e.id
          WHERE e.event_date >= '{BRStart}'
          AND e.event_date <= '{BREnd}'
          AND e.game_id = {game_id}
          AND e.format_id = {format_id}
          AND e.discord_id = {discord_id}
          GROUP BY p.archetype_played
        ) AS BeginningRange ON Decks.archetype_played = BeginningRange.archetype_played
        LEFT OUTER JOIN (
          SELECT p.archetype_played,
            {formula} AS StatER
          FROM participants p
          INNER JOIN events e ON p.event_id = e.id
          WHERE e.event_date >= '{ERStart}'
          AND e.event_date <= '{EREnd}'
          AND e.game_id = {game_id}
          AND e.format_id = {format_id}
          AND e.discord_id = {discord_id}
          GROUP BY p.archetype_played
        ) AS EndingRange ON Decks.archetype_played = EndingRange.archetype_played
        GROUP BY Decks.archetype_played
      )
      WHERE EndingRange >=.02 OR BeginningRange >= .02
      ORDER BY Shift DESC, archetype_played
      """
    
      cur.execute(command)
      rows = cur.fetchall()
      cur.close()
      return rows
