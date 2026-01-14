import tkinter as tk
import random
import math

WIDTTH, HEIGHT = 2560, 1664
DT = 1


class Fish:
    def __init__(self, x, y, angle, speed, ):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.image = random.choice(Fishy_images)

Fishy_images = []

Fishes = []
