"""This builds the image and downscales it for showing the board or any image related processing"""
from PIL import Image, ImageDraw, ImageFont

import libraries.configUtils as configUtils


def constructImage(board, playerColors):
    """
    Returns a rendered board image with the specified resolution from config file
    :param board: The 2x2 array of the board from the JSON
    :param playerColors: An array of all the player colors from the JSON
    """
    filename = 'EmptySquare.png'
    tile = Image.open('textures/' + filename)
    completeImage = None
    for row in board:
        image = None
        for column in row:
            if image is not None:
                if column == 0:
                    image = __stitchTiles(image, tile)
                else:
                    try:
                        tankFileName = 'TankOnBackground.png'
                        tank = Image.open('textures/' + tankFileName)
                        tank = __addTankNumber(tank, column)
                        tank = __recolorTank(tank, playerColors[str(column)])
                        image = __stitchTiles(image, tank)
                    except KeyError:
                        (width1, height1) = tile.size
                        temp = Image.new("RGB", (width1, height1))
                        image = __stitchTiles(image, temp)
            else:
                if column == 0:
                    image = tile
                else:
                    try:
                        tankFileName = 'TankOnBackground.png'
                        tank = Image.open('textures/' + tankFileName)
                        tank = __addTankNumber(tank, column)
                        image = __recolorTank(tank, playerColors[str(column)])
                    except KeyError:
                        (width1, height1) = tile.size
                        image = Image.new("RGB", (width1, height1))
        if completeImage is None:
            completeImage = image
        else:
            completeImage = __stitchRows(image, completeImage)

    completeImage = __rescaleImage(completeImage)
    return completeImage


def __addTankNumber(image, tankNumber):
    if tankNumber < 10:
        img = Image.new('RGBA', (6, 10), color=(255, 255, 255, 0))
    else:
        img = Image.new('RGBA', (12, 10), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), str(tankNumber), fill=(0, 0, 0, 255))
    if tankNumber < 10:
        img = img.resize((60, 100), resample=Image.BOX)
        image.paste(img,
                    (int((image.size[0] / 2) - ((img.size[1] / 2) - 25)), int((image.size[1] / 2) + ((img.size[1] / 2) + 25))),
                    mask=img)
    else:
        img = img.resize((120, 100), resample=Image.BOX)
        image.paste(img,
                    (int((image.size[0] / 2) - ((img.size[1] / 2) + 5)), int((image.size[1] / 2) + ((img.size[1] / 2) + 25))),
                    mask=img)
    return image


def __recolorTank(image, rgbColor):
    newImageData = []
    for color in image.getdata():
        if color == (0, 0, 0, 255):
            newImageData.append((rgbColor[0], rgbColor[1], rgbColor[2], 255))
        else:
            newImageData.append(color)
    newImage = Image.new(image.mode, image.size)
    newImage.putdata(newImageData)
    return newImage


def __stitchTiles(image1, image2):
    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = width1 + width2
    result_height = max(height1, height2)

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(width1, 0))
    return result


def __stitchRows(image1, image2):
    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = max(width1, width2)
    result_height = height1 + height2

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, height1))
    return result


def __rescaleImage(image):
    resolutionValue = int(configUtils.readValue('botSettings', 'boardImageResolution'))
    # TODO One day come back and update this to use dynamic scaling from only 1 axis so that maps can be non-square
    newSize = (resolutionValue, resolutionValue)
    image = image.resize(newSize)
    return image
