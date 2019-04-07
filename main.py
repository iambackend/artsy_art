from PIL import Image, ImageDraw, ImageEnhance
from math import *
from random import *

FRAME_SIZE = 32

def bound(x, a, b):
    return max(min(x, b), a)

class Organism:
    def fatness(self, img):
        parody = self.paint()
        fatness = 0
        for x in range(FRAME_SIZE):
            for y in range(FRAME_SIZE):
                orig = img.getpixel((x, y))
                # paro = parody.getpixel((x, y))
                # print(orig, paro)
                fatness += abs(img.getpixel((x, y)) - parody.getpixel((x, y)))
        return fatness

    def __init__(self, x, y, tilt, first_colour, second_colour):
        self.x, self.y, self.tilt, self.first_colour, self.second_colour = x, y, tilt, first_colour, second_colour

    @classmethod
    def random(cls):
        return cls(randrange(FRAME_SIZE), randrange(FRAME_SIZE), uniform(-pi, pi), randrange(0, 255), randrange(0, 255))

    def mutate(self):
        self.x += randrange(-2, 2)
        self.y += randrange(-2, 2)
        self.tilt += gauss(0, -0.3)
        self.first_colour += bound(randrange(-10, 10), 0, 255)
        self.second_colour += bound(randrange(-10, 10), 0, 255)
        return self

    @staticmethod
    def crossover(a, b):
        prop = uniform(0.3, 0.7)
        return Organism(prop * a.x + (1-prop) * b.x, prop * a.y + (1-prop) * b.y, prop * a.tilt + (1-prop) * b.tilt,
                        int(prop * a.first_colour + (1-prop) * b.first_colour), int(prop * a.second_colour + (1-prop) * b.second_colour))

    def paint(self):
        # print(self.first_colour)
        img = Image.new('L', (FRAME_SIZE, FRAME_SIZE), color=self.first_colour)
        draw = ImageDraw.Draw(img)
        if 0.5 * pi < self.tilt < 1.5 * pi:
            draw.polygon([(-10000000, -10000000), (self.x - cos(self.tilt) * 10000, self.y - sin(self.tilt) * 10000),
                        (self.x + cos(self.tilt) * 10000, self.y + sin(self.tilt) * 10000)], fill=self.second_colour)
        else:
            draw.polygon([(10000000, 10000000), (self.x - cos(self.tilt) * 10000, self.y - sin(self.tilt) * 10000),
                          (self.x + cos(self.tilt) * 10000, self.y + sin(self.tilt) * 10000)], fill=self.second_colour)
        # print(self.x, self.y, self.tilt)
        return img


class Population:
    def __init__(self, img):
        self.img = img

    def solve(self, size, period):
        population = [Organism.random() for i in range(size)]
        sorted(population, key=lambda organism: organism.fatness(self.img))
        # self.img.show()
        for epoch in range(period):
            for i in range(0, size // 3):
                population[i + size // 3] = Organism.crossover(population[i], population[i + 1]).mutate()
            for i in range(size // 3 * 2, size):
                population[i] = Organism.random() #Chernobyl trip
            population = sorted(population, key=lambda organism: organism.fatness(self.img))
            # print([x.fatness(self.img) for x in population])
            # if epoch % 10 == 0:
            #     population[0].paint().show()
        return population[0].paint()

im = Image.open("images/image10.jpg").convert('L')
(width, height) = im.size
# enhancer = ImageEnhance.Color(im)
# im = enhancer.enhance(200000)
# enhancer = ImageEnhance.Contrast(im)
# im = enhancer.enhance(10000)
# enhancer = ImageEnhance.Brightness(im)
# im = enhancer.enhance(0.1)
im.show()

etalon = [[im.crop((x, y, x + FRAME_SIZE, y + FRAME_SIZE)).convert('L') for y in range(0, height, FRAME_SIZE)] for x in range(0, width, FRAME_SIZE)]

result = Image.new('L', (width, height))
# result.save("results/lenna_1_32.png", "PNG")
for i in range(0, width // FRAME_SIZE):
    for j in range(0, height // FRAME_SIZE):
        pop = Population(etalon[i][j])
        result.paste(pop.solve(10, 30), (i * FRAME_SIZE, j * FRAME_SIZE, (i + 1) * FRAME_SIZE, (j + 1) * FRAME_SIZE))
    if i % (width // FRAME_SIZE // 8) == 0:
        result.show()

result.show()
result.save("results/result.png", "PNG")

# for x in range(0, height // FRAME_SIZE):
#     for y in range(0, width // FRAME_SIZE):


