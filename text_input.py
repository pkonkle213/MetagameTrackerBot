import datetime

#TODO: This should be generalized to be used for any text input
async def GetTextInput(bot, message):
  await message.reply("Please enter a date in MM-DD-YYYY format:")

  def check(msg):
      return msg.author == message.author and msg.channel == message.channel

  msg = await bot.wait_for("message", check=check, timeout=30)
  date_str = msg.content
  date_obj = datetime.datetime.strptime(date_str, "%m-%d-%Y").date()
  if date_obj < datetime.date.today() - datetime.timedelta(days=14):
      raise Exception("Date is too far in the past.")
  await message.reply(f"Date set to: {date_obj}")
  return date_obj