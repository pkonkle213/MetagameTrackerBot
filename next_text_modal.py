import discord
from discord import ui, Interaction

class SubmitArchetypeModal(discord.ui.Modal, title='Submit Archetype'):
    # defining a Label with the component set to a Select
    fruit_select = ui.Label(
        text="Your favorite fruit",
        # setting an optional description
        # this will appear below the label on desktop, and below the component on mobile
        description="Please select your favorite fruit from the list.",
        # this is where a select (or TextInput) component goes
        component=ui.Select(
            placeholder="Select your favorite fruit...", # this is optional
            # we can make it optional too using the required kwarg
            # defaults to True (required)
            required=True,
            options=[
                discord.SelectOption(label="Apple", value="apple"),
                discord.SelectOption(label="Banana", value="banana"),
                discord.SelectOption(label="Cherry", value="cherry"),
            ]
        )
    )

    # adding a TextInput for the sake of example
    reason = ui.Label(
        text="Why is that your favorite fruit?",
        component=ui.TextInput(
            placeholder="Tell us why...",
            # making this one optional -- we don't really need to know
            required=False
        )
    )

    # handling the submission
    async def on_submit(self, interaction: Interaction) -> None:
        # will be one of: "apple", "banana", "cherry"
        chosen_fruit = self.fruit_select.component.values[0]
        reason = self.reason.component.value

        # reason is optional so we can handle that here
        if not reason:
            reason = "*you didn't tell us why :(*"

        await interaction.response.send_message(
            f"Your favorite fruit is {chosen_fruit} because {reason}"
        )