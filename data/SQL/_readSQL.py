def read_sql_file(filename: str):
  with open(filename, 'r', encoding='utf-8-sig') as f:
    return f.read()
