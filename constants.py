from collections import namedtuple

Level = namedtuple('Level', ['Number', 'NumEvents', 'Percent'])

Levels = [
    Level('1', 2, 50),
    Level('2', 3, 80),
    Level('3', 4, 95),
    Level('Infinite', 4, 100)
]
