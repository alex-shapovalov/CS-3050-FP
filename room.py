class Room():
    """
    Room is a simple class that represents each room in the map
    When world is instantiated, it procedurally generates rooms

    x: X coordinate of the wall's bottom left corner
    y: Y coordinate of the wall's bottom left corner
    size: The edge length of the room in tiles. Each tile is 80 pyarcade units
    indoor: A room that is not indoor is outdoor
    north, south, east, west: Booleans that represent whether the room has a door on that side or not
    """
    def __init__(self, x, y, size, indoor, north, south, east, west):
        self.x = x
        self.y = y
        self.size = size
        self.indoor = indoor
        self.north = north
        self.south = south
        self.east = east
        self.west = west