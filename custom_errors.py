class CustomError(Exception):
  pass

class EventNotFoundError(CustomError):
  def __init__(self, message):
    self.message = message
    super().__init__(self.message)

class DateRangeError(CustomError):
  def __init__(self, message):
    self.message = message
    super().__init__(self.message)