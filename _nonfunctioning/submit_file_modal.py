import discord


class SubmitFileModal(discord.ui.Modal, title='Submit File'):
  is_submitted = False

  def __init__(self):
    super().__init__()

    self.file_input = discord.ui.Label(
      text="File Upload",
      component=discord.ui.FileUpload(
        #label="Choose a file",
        required=True,  # You can make file upload mandatory
        max_values=1,  # Allows only one file
      ))
  
    self.add_item(self.file_input)

  async def on_submit(self, interaction: discord.Interaction):
    self.is_submitted = True
    uploaded_file = self.file_input.component.values[0]
    print("Uploaded file:\n", uploaded_file)
    print('Type of file:\n', type(uploaded_file))
    await interaction.response.send_message(
      f"Thanks for the upload, {interaction.user.name}!",
      file=uploaded_file,
      ephemeral=True  # Only visible to the user who uploaded
    )

  async def on_error(self, interaction: discord.Interaction,
           error: Exception) -> None:
    await interaction.response.send_message(
      f"Oops! Something went wrong: {error}", ephemeral=True
    )
