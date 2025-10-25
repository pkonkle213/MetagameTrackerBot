store = Store(1210746744602890310,
  'Test Guild',
  'Test Store',
  505548744444477441,
  'Phil',
  True,
  True)
game = Game(1, 'Magic', True)
format = Format(1, 'Pauper', ConvertToDate('1/1/2020'), False)

data = GetMetagame(game, format, '2025-01-01', '2025-12-31', store)
if data is None:
raise Exception("No data found")
dataframe = pd.DataFrame(data, columns=['Archetype', 'Metagame Percent', 'Win Percent'])

print('Dataframe:', dataframe)

fig = plt.figure()
ax = fig.add_subplot()

ax.scatter(dataframe["Metagame Percent"],
dataframe["Win Percent"],
color='blue',
marker='o')

#This wants y to be "archetype"...maybe I need it to start at 1??
for i, y in enumerate(dataframe, 0):
print('i:', i)
print('y:', y)
print('typeof(y):', type(y))
ax.text(i, y + 0.5, f"{y:.2f}", ha='center', va='bottom', fontsize=8)


"""
rect = Rectangle((0.2, 0.75), 0.4, 0.15, color="black", alpha=0.3)
circ = Circle((0.7, 0.2), 0.15, color="blue", alpha=0.3)
pgon = Polygon([[0.15, 0.15], [0.35, 0.4], [0.2, 0.6]], color="green", alpha=0.5)

ax.add_patch(rect)
ax.add_patch(circ)
ax.add_patch(pgon)
"""

# Save this beautiful artwork for posterity!
file_path = "shapes.jpg" #A filename will probably need to be unique as to who generated it and when. Or disposed of once used
fig.savefig(file_path)

with open(file_path, "rb") as f:
pic = discord.File(f, filename=file_path)