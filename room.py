"""
Room is a simple class that represents each room in the map.
When world is instantiated, it procedurally generates rooms.
"""

class Room():

    # x is the x coordinate of the room's bottom left corner.
    # y is the y coordinate of the room's bottom left corner.
    # size is the edge length of the room in pyarcade units.
    # indoor is a boolean. A room that is not indoor is outdoor.
    def __init__(self, x, y, size, indoor):
        self.x = x
        self.y = y
        self.size = size
        self.indoor = indoor

