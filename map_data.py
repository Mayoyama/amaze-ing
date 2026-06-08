from dataclasses import dataclass

TEMP_CONFIG = {
    "width": 50,  # THIS GLOBAL NEEDS TO BE REPLACED BY PARSED DATA
    "height": 50,
    "entry": (1, 4),
    "exit": (44, 43),
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
def temp_data() -> mapData:
    return mapData(**TEMP_CONFIG)


