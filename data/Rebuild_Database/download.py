import psycopg2

# Connect to your PostgreSQL database
conn = psycopg2.connect("dbname=your_db user=your_user password=your_password host=your_host")
cur = conn.cursor()

# Define your query and output file
query = "SELECT * FROM your_table_name"
output_file = "results_2026.csv"

# Use COPY TO STDOUT with CSV HEADER
# The 'WITH CSV HEADER' clause automatically includes column names
copy_query = f"COPY ({query}) TO STDOUT WITH CSV HEADER"

with open(output_file, 'w') as f:
    cur.copy_expert(copy_query, f)

cur.close()
conn.close()
print(f"Data exported successfully to {output_file}")
