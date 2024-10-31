"""
Wall is a simple class that represents each wall.
When a room is created, it will automatically create walls, iff it is an indoor room.
Walls have collision, and will render a texture.
"""

class Wall():

    # x is the x coordinate of the wall's bottom left corner.
    # y is the y coordinate of the wall's bottom left corner.
    # size is the number of tiles wide (horizontal) or tall (vertical) that the wall is.
    # The wall's height or width in pyarcade units is eighty times this value.
    # vertical is a boolean. A wall that is not vertical is horizontal.
    def __init__(self, x, y, size, vertical):
        self.x = x
        self.y = y
        self.size = size
        self.vertical = vertical
