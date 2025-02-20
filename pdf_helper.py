import discord
import PyPDF2

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.content.startswith('!readpdf'):
            if len(message.attachments) > 0:
                attachment = message.attachments[0]
                if attachment.filename.endswith('.pdf'):
                    await attachment.save(attachment.filename)
                    with open(attachment.filename, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        text = ''
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text += page.extract_text()
                    await message.channel.send(text)
                else:
                    await message.channel.send('Please attach a PDF file.')
            else:
                await message.channel.send('Please attach a PDF file.')
