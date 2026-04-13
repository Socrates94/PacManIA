import re

with open('main.py', 'r') as f:
    content = f.read()

# We need to wrap lines 122 to 363 inside a loop
# Wait, Init() is lines 214-250 and load textures
# display() is 287-296
# It's better to keep functions outside the loop

# Let's extract the game loop and wrap it.
