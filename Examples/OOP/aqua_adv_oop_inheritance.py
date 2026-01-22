import tkinter as tk
import random
import math

WIDTH, HEIGHT = 600, 400
DT = 1

FISH_SPEED = 3
FOOD_SPEED = 2

MIN_FISH_DISTANCE = 50
REPULSION_STRENGTH = 0.5
FOOD_ATTRACTION = 0.3

SAND_HEIGHT = 30


class Vector:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k):
        return Vector(self.x * k, self.y * k)

    def __truediv__(self, k):
        return Vector(self.x / k, self.y / k)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def length(self):
        return math.hypot(self.x, self.y)

    def normalized(self):
        l = self.length()
        if l == 0:
            return Vector(0, 0)
        return Vector(self.x / l, self.y / l)

    def project_onto(self, other):
        length_squared = other.dot(other)
        if length_squared == 0:
            return Vector(0, 0)
        scale = self.dot(other) / length_squared
        return other * scale


# --- globální "world": vše v jednom seznamu ---
entities = []


def fishes():
    return [e for e in entities if isinstance(e, Fish) and e.alive]


def foods():
    return [e for e in entities if isinstance(e, Food) and e.alive]


def first_food():
    fl = foods()
    return fl[0] if fl else None


class Entity:
    def __init__(self, canvas, position, velocity=None):
        self.canvas = canvas
        self.position = position      # Vector
        self.velocity = velocity if velocity is not None else Vector(0, 0)
        self.ids = []                 # tkinter item ids
        self.alive = True
        self.half_size = Vector(0, 0) # pro odraz (nastaví potomek)

    def move_graphics(self, delta):
        for item_id in self.ids:
            self.canvas.move(item_id, delta.x, delta.y)

    def bounce_in(self):
        if self.position.x - self.half_size.x < 0 or self.position.x + self.half_size.x > WIDTH:
            self.velocity.x = -self.velocity.x
            self.position.x = max(self.half_size.x, min(WIDTH - self.half_size.x, self.position.x))

        if self.position.y - self.half_size.y < 0 or self.position.y + self.half_size.y > HEIGHT:
            self.velocity.y = -self.velocity.y
            self.position.y = max(self.half_size.y, min(HEIGHT - self.half_size.y, self.position.y))

    def update(self, dt):
        if not self.alive:
            return

        old_pos = self.position
        self.position = self.position + self.velocity * dt
        self.bounce_in()
        delta = self.position - old_pos
        self.move_graphics(delta)

    def destroy(self):
        if not self.alive:
            return
        for item_id in self.ids:
            self.canvas.delete(item_id)
        self.alive = False


class Fish(Entity):
    def __init__(self, canvas, position, color):
        super().__init__(canvas, position, velocity=Vector(random.uniform(-1, 1), random.uniform(-1, 1)))

        # odraz – podle těla (stejně jako původně)
        self.half_size = Vector(25, 12)

        x, y = self.position.x, self.position.y
        body = canvas.create_oval(x - 25, y - 12, x + 25, y + 12, fill=color, outline="")
        tail = canvas.create_polygon(x + 25, y, x + 40, y - 12, x + 40, y + 12, fill=color, outline="")
        eye_white = canvas.create_oval(x - 15, y - 6, x - 7, y + 2, fill="white", outline="")
        eye_black = canvas.create_oval(x - 12, y - 3, x - 9, y, fill="black", outline="")
        self.ids = [body, tail, eye_white, eye_black]

    def limit_speed(self, max_speed):
        speed = self.velocity.length()
        if speed > max_speed:
            self.velocity = self.velocity.normalized() * max_speed

    def apply_separation(self):
        for other in fishes():
            if other is self:
                continue
            displacement = self.position - other.position
            dist = displacement.length()
            if 0 < dist < MIN_FISH_DISTANCE:
                push_dir = displacement / dist
                self.velocity = self.velocity + push_dir * REPULSION_STRENGTH

    def apply_food_attraction(self):
        food = first_food()
        if food is None:
            return
        displacement = food.position - self.position
        dist = displacement.length()
        if dist != 0:
            pull_dir = displacement / dist
            self.velocity = self.velocity + pull_dir * FOOD_ATTRACTION

    def update(self, dt):
        if not self.alive:
            return

        self.apply_separation()
        self.apply_food_attraction()
        self.limit_speed(FISH_SPEED)

        super().update(dt)


class Bubble(Entity):
    def __init__(self, canvas, position, speed):
        super().__init__(canvas, position, velocity=Vector(0, -speed))
        self.half_size = Vector(4, 4)

        x, y = self.position.x, self.position.y
        bid = canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="white", outline="")
        self.ids = [bid]

    def update(self, dt):
        if not self.alive:
            return

        old_pos = self.position
        self.position = self.position + self.velocity * dt

        # respawn dole (bez odrazu)
        if self.position.y + self.half_size.y < 0:
            self.position.x = random.randint(20, WIDTH - 20)
            self.position.y = HEIGHT + self.half_size.y

        delta = self.position - old_pos
        self.move_graphics(delta)


class Food(Entity):
    def __init__(self, canvas, position):
        super().__init__(canvas, position, velocity=Vector(0, FOOD_SPEED))
        self.half_size = Vector(4, 4)
        self.eaten_radius = 20

        x, y = self.position.x, self.position.y
        fid = canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="brown", outline="")
        self.ids = [fid]

    def is_eaten(self):
        for fish in fishes():
            if (self.position - fish.position).length() < self.eaten_radius:
                return True
        return False

    def update(self, dt):
        if not self.alive:
            return

        super().update(dt)

        # sežráno
        if self.is_eaten():
            self.destroy()
            return

        # dopad do písku
        if self.position.y > HEIGHT - SAND_HEIGHT:
            self.destroy()


def create_plant(x):
    for _ in range(random.randint(3, 6)):
        h = random.randint(50, 90)
        offset = random.randint(-10, 10)
        canvas.create_line(
            x + offset, HEIGHT,
            x + offset - random.randint(-15, 15), HEIGHT - h,
            smooth=True, width=3, fill="dark green"
        )


def drop_food(event):
    x = random.randint(20, WIDTH - 20)
    y = 0
    entities.append(Food(canvas, Vector(x, y)))


def animate():
    for e in entities:
        e.update(DT)

    # cleanup (vše v jednom seznamu)
    entities[:] = [e for e in entities if e.alive]

    root.after(30, animate)


root = tk.Tk()
root.title("My Aquarium")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="light blue")
canvas.pack()

# písek
canvas.create_rectangle(
    0, HEIGHT - SAND_HEIGHT,
    WIDTH, HEIGHT,
    fill="#f2d7a1",
    outline=""
)

# kytičky (statika)
for x in range(30, WIDTH, 60):
    create_plant(x)

# ryby
colors = ["orange", "yellow", "pink", "green", "violet", "navy", "lime", "red", "dark red"]
for color in colors:
    x = random.randint(50, WIDTH - 100)
    y = random.randint(50, HEIGHT - 50)
    entities.append(Fish(canvas, Vector(x, y), color))

# bubliny
for _ in range(20):
    x = random.randint(20, WIDTH - 20)
    y = random.randint(HEIGHT - 40, HEIGHT)
    entities.append(Bubble(canvas, Vector(x, y), speed=random.uniform(0.5, 1.5)))

root.bind("<space>", drop_food)

animate()
root.mainloop()
