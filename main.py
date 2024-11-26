import cairo
from math import ceil
from random import randint, random, seed


# Returns image_surface and context with given font and font size
def setup(config, width, height):
    image_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(image_surface)

    # font
    context.select_font_face(*config["FONT"])
    context.set_font_size(config["FONT_SIZE"])

    return image_surface, context


# Attempt to draw the kanji to get the bounding box
def get_coord_info(kanji_string, config):
    # Set width, height to arbitrary value
    # Here we just want the bounding box of the drawn text.
    _, context = setup(config, 1, 1)

    context.set_source_rgb(*config["STROKE_COLOR"])
    context.set_line_width(config["STROKE_WIDTH"])

    context.text_path(kanji_string)

    return context.fill_extents()


def add_fire(kanji_string, config, surface, width, height):
    # DOOM fire array
    rgbs = [
        (0x07, 0x07, 0x07), (0x1F, 0x07, 0x07), (0x2F, 0x0F, 0x07),
        (0x47, 0x0F, 0x07), (0x57, 0x17, 0x07), (0x67, 0x1F, 0x07),
        (0x77, 0x1F, 0x07), (0x8F, 0x27, 0x07), (0x9F, 0x2F, 0x07),
        (0xAF, 0x3F, 0x07), (0xBF, 0x47, 0x07), (0xC7, 0x47, 0x07),
        (0xDF, 0x4F, 0x07), (0xDF, 0x57, 0x07), (0xDF, 0x57, 0x07),
        (0xD7, 0x5F, 0x07), (0xD7, 0x5F, 0x07), (0xD7, 0x67, 0x0F),
        (0xCF, 0x6F, 0x0F), (0xCF, 0x77, 0x0F), (0xCF, 0x7F, 0x0F),
        (0xCF, 0x87, 0x17), (0xC7, 0x87, 0x17), (0xC7, 0x8F, 0x17),
        (0xC7, 0x97, 0x1F), (0xBF, 0x9F, 0x1F), (0xBF, 0x9F, 0x1F),
        (0xBF, 0xA7, 0x27), (0xBF, 0xA7, 0x27), (0xBF, 0xAF, 0x2F),
        (0xB7, 0xAF, 0x2F), (0xB7, 0xB7, 0x2F), (0xB7, 0xB7, 0x37),
        (0xCF, 0xCF, 0x6F), (0xDF, 0xDF, 0x9F), (0xEF, 0xEF, 0xC7),
        (0xFF, 0xFF, 0xFF)
    ]

    one_height = height
    one_width = width // len(kanji_string)

    # generate fire for 1 kanji of size (one_width, one_height)
    grid_height = config["FIRE_GRID_HEIGHT"]
    grid_width = config["FIRE_GRID_WIDTH"]
    grid = [[0 for j in range(grid_width)] for i in range(grid_height)]

    # set last row to white
    for j in range(grid_width):
        grid[grid_height - 1][j] = len(rgbs) - 1

    for i in range(grid_height - 1, 1, -1):
        for j in range(grid_width):
            if grid[i][j] == 0:
                grid[i - 1][j] = 0
            else:
                horz = randint(-1, 1)
                decr = 1 if random() < config["FIRE_DECR_CHANCE"] else 0

                col = j + horz
                if col < 0:
                    col = 0
                elif col >= grid_width:
                    col = grid_width - 1

                grid[i - 1][j] = max(grid[i][col] - decr, 0)

    # clip egg
    alpha = 0.2
    thr = 2

    h, k = grid_width // 2, grid_height // 2
    a, b0 = grid_width / thr, grid_height / thr

    def b(y):
        return b0 * (1 - alpha * (y - k) / b0)

    for i in range(grid_height):
        for j in range(grid_width):
            if ((j - h)**2 / a**2 + (i - k)**2 / b(i)**2) > 0.9:
                grid[i][j] = 0

    data = surface.get_data()

    # draw pixels
    for k in range(len(kanji_string)):
        y_start = (one_height - grid_height) // 2
        x_start = k * one_width + (one_width - grid_width) // 2
        for i in range(grid_height):
            for j in range(grid_width):
                y = y_start + i
                x = x_start + j
                idx = y * surface.get_stride() + x * 4

                color_idx = grid[i][j]

                # ARGB but reversed, so BGRA
                if color_idx >= config["FIRE_DRAW_IDX_MIN"]:
                    data[idx] = rgbs[color_idx][2]
                    data[idx + 1] = rgbs[color_idx][1]
                    data[idx + 2] = rgbs[color_idx][0]
                    data[idx + 3] = 255

    return surface


def generate_image(kanji_string, config):
    image_surface = generate_image_surface(kanji_string, config)
    image_surface.write_to_png("main.png")


def generate_image_surface(kanji_string, config):
    x1, y1, x2, y2 = get_coord_info(kanji_string, config)

    # calculate image dimensions
    height = ceil(y2 - y1 + 2 * config["PADDING"])
    width = ceil(x2 - x1 + 2 * config["PADDING"])

    # add fire padding
    height_padding = ceil(config["FIRE_PADDING"] * height)
    height += height_padding

    image_surface, context = setup(config, width, height)

    # transparency
    context.set_source_rgba(1, 1, 1, 0)
    context.paint()

    # add fire
    image_surface = add_fire(kanji_string, config, image_surface, width, height)

    # start position
    startX = -x1 + config["PADDING"]
    startY = -y1 + config["PADDING"]
    context.move_to(startX, startY + height_padding // 2)

    # stroke
    context.set_source_rgb(*config["STROKE_COLOR"])
    context.set_line_width(config["STROKE_WIDTH"])
    context.text_path(kanji_string)
    context.stroke_preserve()

    # fill
    context.set_source_rgb(*config["FILL_COLOR"])
    context.fill()

    return image_surface


def main():
    config = {
        # font
        "FONT": ("Noto Sans Math", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
        "FONT_SIZE": 100,
        "STROKE_WIDTH": 2,
        "STROKE_COLOR": (0, 0, 0),
        "FILL_COLOR": (1, 0.65, 0),

        # misc
        "PADDING": 5,

        # fire
        "FIRE_PADDING": 0.8,
        "FIRE_DECR_CHANCE": 0.25,
        "FIRE_DRAW_IDX_MIN": 4,
        "FIRE_GRID_HEIGHT": 157,
        "FIRE_GRID_WIDTH": 90
    }

    seed(42)

    kanji_string = "ℝ"
    generate_image(kanji_string, config)


if __name__ == "__main__":
    main()

