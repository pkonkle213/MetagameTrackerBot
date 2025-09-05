select event_date, cg.name as game_name, f.name as format_name, archetype_played, wins, losses, draws
  from full_standings fp
  inner join events e on e.id = fp.event_id
  inner join cardgames cg on cg.id = e.game_id
  inner join formats f on f.id = e.format_id
  inner join player_names pn on pn.discord_id = e.discord_id and pn.player_name = fp.player_name
inner join unique_archetypes uar on uar.event_id = e.id and uar.player_name = pn.player_name
  where pn.submitter_id = '153591222148136970'
  and e.discord_id = '1210746744602890310'
  order by e.event_date desc