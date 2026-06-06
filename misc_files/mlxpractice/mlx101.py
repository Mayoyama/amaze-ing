from mlx import Mlx as MlxClass

mlx = MlxClass()

mlx_ptr = mlx.mlx_init()
win = mlx.mlx_new_window(mlx_ptr, 800, 600, "test")

def key_handler(keycode, param):
    print("KEY:", keycode)

    mlx.mlx_loop_exit(mlx_ptr)


img = mlx.mlx_new_image(mlx_ptr, 100, 100)

data, bpp, size_line, fmt = mlx.mlx_get_data_addr(img)

x = 50
y = 50

offset = y * size_line + x * 4

data[offset + 0] = 0
data[offset + 1] = 0
data[offset + 2] = 255
data[offset + 3] = 255

print(data[offset + 0])
print(data[offset + 1])
print(data[offset + 2])
print(data[offset + 3])

mlx.mlx_put_image_to_window(
    mlx_ptr,
    win,
    img,
    100,
    100
)

mlx.mlx_key_hook(
    win,
    key_handler,
    None
)

mlx.mlx_loop(mlx_ptr)
