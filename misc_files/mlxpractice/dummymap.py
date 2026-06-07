# from mlx import Mlx as mx # pyright: ignore[reportMissingImports]

CELL_SIZE = 20



if __name__ == "__main__":
    grid = [
        [15, 10],
        [5,  3]
    ]

    wall_check = [has_N_wall, has_E_wall, has_S_wall, has_W_wall]
    for check in wall_check:
        if check(15):
            print("Yes")

    print(cell_pos(3, 5))
    
    for 




'''
 __
|__|__|
 __   |
'''
