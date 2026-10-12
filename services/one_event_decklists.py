from custom_errors import KnownError
from tuple_conversions import Event
from discord import Embed, app_commands, Interaction
from discord.ext import commands
from data.event_decklists_data import GetDecks, GetDecklists
from views.pagination_view import PaginationView


async def OneEventDecklists(interaction: Interaction, event: Event) -> None:
    decklist_output = []
    # 1) Get all decks from the event
    decks = await GetDecks(event)
    if len(decks) == 0:
        raise KnownError("No decks found")

    # 2) For all decks, make a list of ids

    # 3) Get all decklists for those decks
    decklists = await GetDecklists(event)

    # 4) For each deck, create the title of '{archetype} ({wins} - {losses} - {draws})'
    # 5) For each deck, create a list of cards like:
    for deck in decks:
        title = f"{deck.archetype_played} ({deck.wins} - {deck.losses} - {deck.draws})"
        mainboard_list = [
            f"{card.quantity} {card.card_name}"
            for card in decklists
            if card.deck_id == deck.id and card.is_mainboard
        ]
        mainboard = "\n".join(mainboard_list)

        sideboard_list = [
            f"{card.quantity} {card.card_name}"
            for card in decklists
            if card.deck_id == deck.id and not card.is_mainboard
        ]
        sideboard = "\n".join(sideboard_list)

        description = (
            f"Mainboard\n---------\n{mainboard}\n\nSideboard\n---------\n{sideboard}"
        )
        embed = Embed(title=title, description=description)

        # 6) Assign to a list of embeds, initialize view, and send
        decklist_output.append(embed)

    if len(decklist_output) < 1:
        raise KnownError("No decklists found for this event")

    view = PaginationView(decklist_output)
    initial_embed = decklist_output[0]
    initial_embed.set_footer(text=f"Page 1 of {len(decklist_output)}")
    await interaction.followup.send(embed=initial_embed, view=view, ephemeral=True)
