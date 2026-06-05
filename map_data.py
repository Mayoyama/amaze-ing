from dataclasses import dataclass

TEMP_CONFIG = {
    "width": 21,  # THIS GLOBAL NEEDS TO BE REPLACED BY PARSED DATA
    "height": 21,
    "entry": (2, 10),
    "exit": (10, 2),
    "output_file": "",
    "seed": 42,
    "perfect": True
}

@dataclass
class mapData:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    seed: int
    perfect: bool


'''
insert parse function from config.txt
'''
def temp_data() -> dataclass:
    return mapData(**TEMP_CONFIG)


