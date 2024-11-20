import cairo
from math import ceil


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


def generate_image(kanji_string, config):
    x1, y1, x2, y2 = get_coord_info(kanji_string, config)

    # calculate image dimensions
    height = ceil(y2 - y1 + 2 * config["PADDING"])
    width = ceil(x2 - x1 + 2 * config["PADDING"])

    image_surface, context = setup(config, width, height)

    # transparency
    context.set_source_rgba(1, 1, 1, 0)
    context.paint()

    # start position
    startX = -x1 + config["PADDING"]
    startY = -y1 + config["PADDING"]
    context.move_to(startX, startY)

    # stroke
    context.set_source_rgb(*config["STROKE_COLOR"])
    context.set_line_width(config["STROKE_WIDTH"])
    context.text_path(kanji_string)
    context.stroke_preserve()

    # fill
    context.set_source_rgb(*config["FILL_COLOR"])
    context.fill()

    image_surface.write_to_png("main.png")


def main():
    config = {
        # font
        "FONT": ("Noto Serif JP", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
        "FONT_SIZE": 100,
        "STROKE_WIDTH": 2,
        "STROKE_COLOR": (0, 0, 0),
        "FILL_COLOR": (1, 0.65, 0),

        # misc
        "PADDING": 5
    }

    kanji_string = "我武者羅"
    generate_image(kanji_string, config)


main()

