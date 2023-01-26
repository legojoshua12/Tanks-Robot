"""This builds the image and downscales it for showing the board or any image related processing"""
from pathlib import Path
from PIL import Image, ImageDraw

from src.tanks.libraries import configUtils as configUtils


def construct_image(board, player_colors):
    """
    Returns a rendered board image with the specified resolution from config file
    :param board: The 2x2 array of the board from the JSON
    :param player_colors: An array of all the player colors from the JSON
    """
    try:
        image_path = Path(__file__).resolve().parent / 'textures/EmptySquare.png'
        tile = Image.open(image_path)
    except FileNotFoundError:
        try:
            image_path = 'src/tanks/textures/EmptySquare.png'
            tile = Image.open(image_path)
        except FileNotFoundError:
            raise FileNotFoundError("Could not locate textures folder!")
    complete_image = None
    for row in board:
        image = None
        for column in row:
            if image is not None:
                if column == 0:
                    image = __stitch_tiles(image, tile)
                else:
                    try:
                        try:
                            image_path = Path(__file__).resolve().parent / 'textures/TankOnBackground.png'
                            tank = Image.open(image_path)
                        except FileNotFoundError:
                            try:
                                image_path = 'src/tanks/textures/TankOnBackground.png'
                                tank = Image.open(image_path)
                            except FileNotFoundError:
                                raise FileNotFoundError('Could not locate tank background in textures folder!')
                        tank = __add_tank_number(tank, column)
                        tank = __recolor_tank(tank, player_colors[str(column)])
                        image = __stitch_tiles(image, tank)
                    except KeyError:
                        (width1, height1) = tile.size
                        temp = Image.new("RGB", (width1, height1))
                        image = __stitch_tiles(image, temp)
            else:
                if column == 0:
                    image = tile
                else:
                    try:
                        try:
                            image_path = Path(__file__).resolve().parent / 'textures/TankOnBackground.png'
                            tank = Image.open(image_path)
                        except FileNotFoundError:
                            try:
                                image_path = 'src/tanks/textures/TankOnBackground.png'
                                tank = Image.open(image_path)
                            except FileNotFoundError:
                                raise FileNotFoundError('Could not locate tank background in textures folder!')
                        tank = __add_tank_number(tank, column)
                        image = __recolor_tank(tank, player_colors[str(column)])
                    except KeyError:
                        (width1, height1) = tile.size
                        image = Image.new("RGB", (width1, height1))
        if complete_image is None:
            complete_image = image
        else:
            complete_image = __stitch_rows(image, complete_image)

    complete_image = __rescale_image(complete_image)
    return complete_image


def __add_tank_number(image, tank_number):
    if tank_number < 10:
        img = Image.new('RGBA', (6, 10), color=(255, 255, 255, 0))
    else:
        img = Image.new('RGBA', (12, 10), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), str(tank_number), fill=(0, 0, 0, 255))
    if tank_number < 10:
        img = img.resize((60, 100), resample=Image.BOX)
        image.paste(img,
                    (int((image.size[0] / 2) - ((img.size[1] / 2) - 25)), int((image.size[1] / 2) + ((img.size[1] / 2)
                                                                                                     + 25))), mask=img)
    else:
        img = img.resize((120, 100), resample=Image.BOX)
        image.paste(img,
                    (int((image.size[0] / 2) - ((img.size[1] / 2) + 5)), int((image.size[1] / 2) + ((img.size[1] / 2)
                                                                                                    + 25))), mask=img)
    return image


def __recolor_tank(image, rgb_color):
    new_image_data = []
    for color in image.getdata():
        if color == (0, 0, 0, 255):
            new_image_data.append((rgb_color[0], rgb_color[1], rgb_color[2], 255))
        else:
            new_image_data.append(color)
    new_image = Image.new(image.mode, image.size)
    new_image.putdata(new_image_data)
    return new_image


def __stitch_tiles(image1, image2):
    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = width1 + width2
    result_height = max(height1, height2)

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(width1, 0))
    return result


def __stitch_rows(image1, image2):
    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = max(width1, width2)
    result_height = height1 + height2

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, height1))
    return result


def __rescale_image(image):
    resolution_value = int(configUtils.read_value('botSettings', 'boardImageResolution'))
    # TODO One day come back and update this to use dynamic scaling from only 1 axis so that maps can be non-square
    new_size = (resolution_value, resolution_value)
    image = image.resize(new_size)
    return image
