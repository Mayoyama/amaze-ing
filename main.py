#  Dummy data until parsing is finished

STARTING_CONFIG = {
    "width": 21,  # Tip: Stick to odd numbers for grid-based wall carving
    "height": 21,
    "entry": (0, 1),
    "exit": (20, 19),
    "seed": 42
}


# A map of directions to: (row_offset, col_offset, wall_bit, opposite_wall_bit)
DIRECTIONS = {
    "N": (-1,  0, 1, 4),  # Moving North changes row by -1, clears bit 1. Opposite is South (4)
    "E": ( 0,  1, 2, 8),  # Moving East changes col by +1, clears bit 2. Opposite is West (8)
    "S": ( 1,  0, 4, 1),  # Moving South changes row by +1, clears bit 4. Opposite is North (1)
    "W": ( 0, -1, 8, 2),  # Moving West changes col by -1, clears bit 8. Opposite is East (2)
}
