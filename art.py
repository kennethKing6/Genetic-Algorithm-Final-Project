import random
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFile

chromosomes = 1500
population = 50
iterations = 10000

canvas_width = 100
canvas_height = 100

# will not throw error
FILEPATH = os.path.abspath(__file__)
FILEDIR = FILEPATH.replace(os.path.basename(FILEPATH),'')
ImageFile.LOAD_TRUNCATED_IMAGES = True

# path to image
image_path = os.path.join(FILEDIR, 'Mona_Lisa.jpg')

# open the image
image = Image.open(image_path)


# calculate the triangle area using vertices
def getArea(x1, x2, x3, y1, y2, y3):
    return abs(1/2 * (x1*y2 + x2*y3 + x3*y1 - x1*y3 - x2*y1 - x3*y2))

# create triangle
def create_triangle(points, color, img):
    d = ImageDraw.Draw(img)
    d.polygon(points, fill=color)

def difference(original_img, new_img):
    width, height = original_img.size
    new_width, new_height = new_img.size
    if (new_width != width or new_height != height):
        print("Error, different picture size!")
        exit()

    # reshape the array into 3d structure with 3 RGB color (Red, Green, Blue)
    pic_1 = np.array(original_img, dtype=np.uint64).reshape((height, width, 3))[:, :, 3]
    pic_2 = np.array(new_img, dtype=np.uint64).reshape(new_height, new_width, 3)
    # sum difference need to be focused on color
    return np.sqrt(np.square(pic_1 - pic_2).sum(axis=-1)).sum()

def random_position(canvas_width, canvas_height):
    return (random.randint(0, canvas_width), random.randint(0, canvas_height))

# if there is no prebest then each color will be adding another random number to change the gradient
def random_color(prebest=None):
    if not prebest:
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    else:
        return (prebest[3][0] + random.randint(-200, 200) + prebest[3][1] + random.randint(-200, 200) + prebest[3][2] + random.randint(-200, 200))

