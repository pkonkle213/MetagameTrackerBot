from settings import DATABASE_URL
import discord
from discord.ext import commands
import psycopg
import pandas as pd
import io

def DatabaseCommandsDownload():
  with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
      cur.execute("""
          SELECT table_name 
          FROM information_schema.tables 
          WHERE table_schema = 'public'
      """)
      tables = [row[0] for row in cur.fetchall()]
  
    # 3. Create an in-memory buffer for the Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore[arg-type]
      for table in tables:
          # Load each table into a Pandas DataFrame
          df = pd.read_sql(f"SELECT * FROM {table}", conn)
          # Write to a specific sheet named after the table
          df.to_excel(writer, sheet_name=table, index=False)
  
    # 4. Reset buffer position and send to Discord
    output.seek(0)
    file = discord.File(fp=output, filename="database_export.xlsx")
    
    return file