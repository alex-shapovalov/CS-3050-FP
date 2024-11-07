"""
Wall is a simple class that represents a wall.
When room is instantiated, it automatically creates walls.
"""

class Room():

    # x is the x coordinate of the wall's bottom left corner.
    # y is the y coordinate of the wall's bottom left corner.
    # size is the edge length of the room in tiles. Each tile is 80 pyarcade units.
    # veritcal is a boolean. A wall that is not vertical is horizontal.
    def __init__(self, x, y, size, veritcal):
        self.x = x
        self.y = y
        self.size = size
        self.veritcal = veritcal
