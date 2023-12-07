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


def drawOutlined(triangle, outline_color, thickness, img, name):
    draw = ImageDraw.Draw(img)
    draw.polygon(triangle[:3],fill=triangle[3])
    draw.line((triangle[0],triangle[1],triangle[2],triangle[0]),outline_color,thickness)
    img.save(name)

# this part can modify
def convert_size(img, dh):
    w, h = img.size
    print("resizing from {}/{}".format(w,h))

    hRatio = dh/h
    dw = int(w*hRatio)
    img = img.resize((dw, dh), Image.Resampling.LANCZOS)

    print("resized to {}/{}".format(dw,dh))
    return img

def check_area(list, img):
    for i in list:
        try:
            x = img[i[0],i[1]]
        except:
            return False
    return True

def get(w, h, img):
    rand1 = random_position(w, h)
    rand2 = (rand1[0] + random.randint(-100, 100), rand1[1] + random.randint(-100, 100))
    rand3 = (rand2[0] + random.randint(-100, 100), rand2[1] + random.randint(-100, 100))

    area = getArea(rand1[0], rand1[0], rand2[0], rand2[1], rand3[0], rand3[1])

    # The triangle shape relative to image area should not exceed 3%
    if area / (w * h) * 100 > 3 or not check_area([rand1, rand2, rand3], img):
        return get(w, h, img)
    return (rand1, rand2, rand3)

    try:
        original_img = convert_size(Image.open(FILEDIR+'Mona_lisa', 'r'), 160)
    except FileNotFoundError:
        print("Image file not found!")
        exit()

    w, h = original_img.size

    blank = Image.new('RGB', (w, h), (255, 255, 255))
    cycles = 0
    generations = 0
    Bests = []
    Scores = []
    imgList = []

    try:
        m = Image.open(FILEDIR + 'best.png', 'r')
        if (w, h) != m.size:
            blank.save(FILEDIR + 'best.png')
            blank.save(FILEDIR + 'gbest.png')
    except FileNotFoundError:
        blank.save(FILEDIR + 'best.png')

    try:
        Best = Image.open(FILEDIR + 'best.png')
        m = open(FILEDIR + 'gbest.png', 'r')
        Scores.append(difference(original_img, Best))
    except FileNotFoundError:
        blank.save(FILEDIR + 'gbest.png')

    Draw = ImageDraw.Draw(Best)

    accuracy = 5
    if accuracy > 999:
        print('[!] The accuracy cannot be over 999!')
        exit()

    cycleRate = accuracy * 2
    colorTry = round(accuracy / 2.0)

    while True:
        RM = Image.open(FILEDIR + 'best.png').load()
        GhostBest = Image.new('RGB', (w, h), (255, 255, 255))
        GG = GhostBest.load()

        for x1 in range(w):
            for y1 in range(h):
                GG[x1, y1] = RM[x1, y1]
        count = 0

        jobs = []
        print('start generation')
        for i1 in range(cycleRate):

            Norm = Image.open(FILEDIR + 'best.png')

            rand = get(w, h, GG)

            for i2 in range(colorTry):
                if Bests == []:
                    col = random_color()
                else:
                    zBests = list(Bests)
                    zBests.reverse()
                    col = random_color(zBests[0])

                create_triangle(rand, col, Norm)
                imgList.append([difference(original_img, Norm), (rand[0], rand[1], rand[2], col)])
            cycles += 1
            count += 1

        b = 10 ** 62
        b1 = []

        for i1 in imgList:
            if i1[0] < b:
                b = i1[0]
                b1 = i1[1]

        Bests.append(b1)

        DrawG = ImageDraw.Draw(GhostBest)
        DrawG.polygon(b1[:3], fill=b1[3])
        GhostBest.save(FILEDIR + 'gbest.png')
        scoreG = difference(original_img, GhostBest)

        if len(Scores) != 0:
            if scoreG <= Scores[len(Scores) - 1]:
                Draw.polygon(b1[:3], fill=b1[3])
                Best.save(FILEDIR + 'best.png')
            else:
                Best.save(FILEDIR + 'best.png')
                continue
        else:
            Draw.polygon(b1[:3], fill=b1[3])
            Best.save(FILEDIR + 'best.png')

        drawOutlined(b1, (255, 0, 0), 3, GhostBest, FILEDIR + 'gbest.png')
        GhostBest.save(FILEDIR + 'gbest.png')
        imgList = []
        generations += 1

        scoreR = difference(original_img, Best)
        print('\n\n--------------------\n\nGeneration: %s \tCycles: %s\t Chose Best. Image error: %s' % (
        generations, cycles, scoreR))
        Scores.append(scoreR)


