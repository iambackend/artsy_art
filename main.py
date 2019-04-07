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
                fatness += abs(img.getpixel((x, y)) - parody.getpixel((x, y)))
        return fatness

    def __init__(self, x, y, tilt, first_colour, second_colour):
        self.x, self.y, self.tilt, self.first_colour, self.second_colour = x, y, tilt, first_colour, second_colour

    @classmethod
    def random(cls):
        return cls(randrange(block_size), randrange(block_size), uniform(-pi, pi), randrange(0, 255), randrange(0, 255))

    def mutate(self):
        self.x = bound(self.x + randrange(-2, 2), -2, block_size + 2)
        self.y = bound(self.y + randrange(-2, 2), -2, block_size + 2)
        self.tilt = (self.tilt + gauss(0, 0.3)) % 2*pi
        self.first_colour += bound(randrange(-10, 10), 0, 255)
        self.second_colour += bound(randrange(-10, 10), 0, 255)
        return self

    @staticmethod
    def crossover(a, b):
        prop = uniform(0.3, 0.7)
        return Organism(prop * a.x + (1-prop) * b.x, prop * a.y + (1-prop) * b.y, prop * a.tilt + (1-prop) * b.tilt,
                        int(prop * a.first_colour + (1-prop) * b.first_colour), int(prop * a.second_colour + (1-prop) * b.second_colour))

    def paint(self):
        img = Image.new('L', (block_size, block_size), color=self.first_colour)
        draw = ImageDraw.Draw(img)
        if 0.5 * pi < self.tilt < 1.5 * pi:
            draw.polygon([(-10000000, -10000000), (self.x - cos(self.tilt) * 10000, self.y - sin(self.tilt) * 10000),
                        (self.x + cos(self.tilt) * 10000, self.y + sin(self.tilt) * 10000)], fill=self.second_colour)
        else:
            draw.polygon([(10000000, 10000000), (self.x - cos(self.tilt) * 10000, self.y - sin(self.tilt) * 10000),
                          (self.x + cos(self.tilt) * 10000, self.y + sin(self.tilt) * 10000)], fill=self.second_colour)
        return img


class Population:
    def __init__(self, img):
        self.img = img

    def solve(self, size, generations):
        population = [Organism.random() for i in range(size)]
        sorted(population, key=lambda organism: organism.fatness(self.img))
        for epoch in range(generations):
            for i in range(0, size // 3):
                population[i + size // 3] = Organism.crossover(population[i], population[i + 1]).mutate()
            for i in range(size // 3 * 2, size):
                population[i] = Organism.random() #Chernobyl trip
            population = sorted(population, key=lambda organism: organism.fatness(self.img))
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

# image_path = 'Lenna.png'

im = Image.open("images/" + image_path).convert('L')
(width, height) = im.size
im.show()

etalon = [[im.crop((x, y, x + block_size, y + block_size)) for y in range(0, height, block_size)] for x in range(0, width, block_size)]

result = Image.new('L', (width, height))

def solver(orig):
    pop = Population(orig)
    return pop.solve(population_size, generations)

from multiprocessing import Pool
with Pool(4) as p:
    for i in range(0, width // block_size):
        resultt = p.map(solver, etalon[i])
        for j in range(0, height // block_size):
            result.paste(resultt[j], (i * block_size, j * block_size, (i + 1) * block_size, (j + 1) * block_size))
        print(str((i + 1) / (width // block_size) * 100) + '% is done')

result.show()
result.save("results/" + str(block_size) + "_" + str(population_size) + "_" + str(generations) + "_" + image_path)



