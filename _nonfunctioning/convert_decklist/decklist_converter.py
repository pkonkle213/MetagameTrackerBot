"""
My thoughts on how to convert a decklist:
  1. Get the decklist from the user
  2. Convert the decklist to a format that can be used by the bot
  3. Retrieve the rules for archetypes
  4. Go through each archetype 
    4.1. Does the list of cards contain the cards the archetype IS 
    4.2. Does the list of cards not contain the cards the archetype IS NOT
  5. After determining the archetype (or label it as 'OTHER'), save the decklist to the database linked to the archetype submission by ID (which I just removed, great)
"""

"""
Things needed:
  1. I need to make a database of rules. What archetype names are, what cards define them, and what cards specifically differ them from similar archetypes.
  This has been done before (https://github.com/Badaro/MTGOArchetypeParser), but I need to put my spin on it, specifically for pauper.
  2. I need to give archetype submissions an ID again, as a decklist will be linked to it
  3. I'll need more tables to store cards and decklists.
    3.1. One table for cards (ID, Name) - This will eliminate redundant entries in my table (lots of islands!)
    3.2. One table for decklists (ArchetypeSubmissionID, CardID, Quantity)
  4. Better examples of decks to test against
    4.1. I need at least two distinct archetypes that are easy to tell from each other (bogles vs spy)
    4.2. I need at least two distinct archetypes that are hard to tell from each other (White Weenie vs Boros Bully, Elves vs Spy, Mono Red Madness vs Rakdos Madness, Mono Blue Terror vs Dimir Terror, Mono Blue Faeries vs Dimir Faeries vs Izzet Faeries)
"""