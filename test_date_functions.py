from date_functions import ConvertToDate

def test_ConvertToDate():
  assert ConvertToDate('12/12/2022') == '2022-12-12'