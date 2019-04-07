from PIL import Image, ImageDraw, ImageEnhance
from math import *
from random import *

def bound(x, a, b):
    return max(min(x, b), a)

class Organism:
    def fatness(self, img):
        parody = self.paint()
        fatness = 0
        for x in range(block_size):
            for y in range(block_size):
                orig = img.getpixel((x, y))
                paro = parody.getpixel((x, y))
                # print(orig, paro)
                fatness += abs(orig[0] - paro[0])**2 + abs(orig[1] - paro[1])**2 + abs(orig[2] - paro[2])**2
        return fatness

    def __init__(self, x, y, tilt, first_colour, second_colour):
        self.x, self.y, self.tilt, self.first_colour, self.second_colour = x, y, tilt, first_colour, second_colour

    @classmethod
    def random(cls):
        return cls(randrange(block_size), randrange(block_size), uniform(-pi, pi),
                   (randrange(0, 255), randrange(0, 255), randrange(0, 255)),
                   (randrange(0, 255), randrange(0, 255), randrange(0, 255)))

    def mutate(self):
        self.x += randrange(-2, 2)
        self.y += randrange(-2, 2)
        self.tilt += gauss(0, -0.3)
        self.first_colour = (bound(self.first_colour[0] + randrange(-10, 10), 0, 255),
                             bound(self.first_colour[1] + randrange(-10, 10), 0, 255),
                             bound(self.first_colour[2] + randrange(-10, 10), 0, 255))
        self.second_colour = (bound(self.second_colour[0] + randrange(-10, 10), 0, 255),
                              bound(self.second_colour[1] + randrange(-10, 10), 0, 255),
                              bound(self.second_colour[2] + randrange(-10, 10), 0, 255))
        return self

    @staticmethod
    def crossover(a, b):
        prop = uniform(0.3, 0.7)
        return Organism(prop * a.x + (1-prop) * b.x, prop * a.y + (1-prop) * b.y, prop * a.tilt + (1-prop) * b.tilt,
                        (int(prop * a.first_colour[0] + (1-prop) * b.first_colour[0]),
                         int(prop * a.first_colour[1] + (1 - prop) * b.first_colour[1]),
                         int(prop * a.first_colour[2] + (1 - prop) * b.first_colour[2])),
                        (int(prop * a.second_colour[0] + (1 - prop) * b.second_colour[0]),
                         int(prop * a.second_colour[1] + (1 - prop) * b.second_colour[1]),
                         int(prop * a.second_colour[2] + (1 - prop) * b.second_colour[2])))

    def paint(self):
        # print(self.first_colour)
        img = Image.new('RGB', (block_size, block_size), color=self.first_colour)
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

    def solve(self, size, generations):
        population = [Organism.random() for i in range(size)]
        sorted(population, key=lambda organism: organism.fatness(self.img))
        # self.img.show()
        for epoch in range(generations):
            for i in range(0, size // 3):
                population[i + size // 3] = Organism.crossover(population[i], population[i + 1]).mutate()
            for i in range(size // 3 * 2, size):
                population[i] = Organism.random() #Chernobyl trip
            population = sorted(population, key=lambda organism: organism.fatness(self.img))
            # print([x.fatness(self.img) for x in population])
            # if epoch % 10 == 0:
            #     population[0].paint().show()
        return population[0].paint()

import sys

if len(sys.argv) != 5:
    print("You are dumbass, run program in following format:\n"
          "python3 main.py image_path size_of_block population_size generations\n"
          "I recommend you following parameters:\n"
          "image_path: name of file in images directory, otherwise it will not work"
          "size_of_block: 8/16/32, 1 will be just extremly slow convertion to bw\n"
          "population: 10 is ok, never tried other values\n"
          "generations: 10-30 is ok\n")
    sys.exit(-1)

image_path = sys.argv[1]
block_size = int(sys.argv[2])
population_size = int(sys.argv[3])
generations = int(sys.argv[4])

im = Image.open("images/" + image_path).convert('RGB')
(width, height) = im.size
# enhancer = ImageEnhance.Color(im)
# im = enhancer.enhance(200000)
# enhancer = ImageEnhance.Contrast(im)
# im = enhancer.enhance(10000)
# enhancer = ImageEnhance.Brightness(im)
# im = enhancer.enhance(0.1)
im.show()

etalon = [[im.crop((x, y, x + block_size, y + block_size)) for y in range(0, height, block_size)] for x in range(0, width, block_size)]

result = Image.new('RGB', (width, height))
# result.save("results/lenna_1_32.png", "PNG")
for i in range(0, width // block_size):
    for j in range(0, height // block_size):
        pop = Population(etalon[i][j])
        result.paste(pop.solve(population_size, generations), (i * block_size, j * block_size, (i + 1) * block_size, (j + 1) * block_size))
    if i % (width // block_size // 8) == 0:
        result.show()

result.show()
result.save("results/RGB_z" + str(block_size) + "_" + str(population_size) + "_" + str(generations) + "_" + image_path)

# for x in range(0, height // FRAME_SIZE):
#     for y in range(0, width // FRAME_SIZE):


