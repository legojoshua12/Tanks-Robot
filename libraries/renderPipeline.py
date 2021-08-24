from PIL import Image

import libraries.configUtils as configUtils


def constructImage(board, playerColors):
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
                    # TODO Update this to use a tank image
                    try:
                        tankFileName = 'TankOnBackground.png'
                        tank = Image.open('textures/' + tankFileName)
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
                    # TODO Update this to use a tank image
                    (width1, height1) = tile.size
                    image = Image.new("RGB", (width1, height1))
        if completeImage is None:
            completeImage = image
        else:
            completeImage = __stitchRows(image, completeImage)

    completeImage = __rescaleImage(completeImage)
    return completeImage


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
