import json

# Opening JSON file
import boardConstructor

f = open('ExampleGames.json', )

# returns JSON object as
# a dictionary
data = json.load(f)

# Iterating through the json
# list
board = data['games']['server#6789']['channel#3456']['board']
for row in range(len(board)):
    print(board[row])

# Closing file
f.close()