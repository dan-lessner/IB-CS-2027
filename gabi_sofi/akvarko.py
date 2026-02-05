import tkinter as tk
import random
import math

WIDTH, HEIGHT = 600, 400
FISH_SPEED = 3
FOOD_SPEED = 2

MIN_FISH_DISTANCE = 50
REPULSION_STRENGTH = 0.5
FOOD_ATTRACTION = 0.3

root = tk.Tk()
root.title("My Aquarium")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="light blue")
canvas.pack()

# písek dole
SAND_HEIGHT = 30
canvas.create_rectangle(
    0, HEIGHT - SAND_HEIGHT,
    WIDTH, HEIGHT,
    fill="#f2d7a1",
    outline=""
)

colors = ["orange", "yellow", "pink", "green", "violet", "navy", "lime", "red", "dark red"]
fish_list = []
bubble_list = []
food_list = []

def create_fish(x, y, color):
    body = canvas.create_oval(x - 25, y - 12, x + 25, y + 12, fill=color, outline="")
    tail = canvas.create_polygon(x + 25, y, x + 40, y - 12, x + 40, y + 12, fill=color, outline="")
    eye_white = canvas.create_oval(x - 15, y - 6, x - 7, y + 2, fill="white", outline="")
    eye_black = canvas.create_oval(x - 12, y - 3, x - 9, y, fill="black", outline="")
    return [body, tail, eye_white, eye_black]

# 🔁 FLIP FUNCTION (NEW)
def flip_fish(fish):
    fish["dir"] *= -1
    cx = fish["x"]

    for part in fish["parts"]:
        coords = canvas.coords(part)
        for i in range(0, len(coords), 2):
            coords[i] = 2 * cx - coords[i]
        canvas.coords(part, coords)

# vytvoření rybiček
for color in colors:
    x = random.randint(50, WIDTH - 100)
    y = random.randint(50, HEIGHT - 50)
    parts = create_fish(x, y, color)

    fish_list.append({
        "x": x,
        "y": y,
        "vx": random.uniform(-1, 1),
        "vy": random.uniform(-1, 1),
        "parts": parts,
        "dir": 1   # 1 = right, -1 = left
    })

# kytičky
def create_plant(x):
    for _ in range(random.randint(3, 6)):
        height = random.randint(50, 90)
        offset = random.randint(-10, 10)
        canvas.create_line(
            x + offset, HEIGHT,
            x + offset - random.randint(-15, 15), HEIGHT - height,
            smooth=True, width=3, fill="dark green"
        )

for x in range(30, WIDTH, 60):
    create_plant(x)

# bublinky
for _ in range(20):
    x = random.randint(20, WIDTH - 20)
    y = random.randint(HEIGHT - 40, HEIGHT)
    bubble = canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="white", outline="")
    bubble_list.append({"id": bubble, "speed": random.uniform(0.5, 1.5)})

# jídlo
def drop_food(event):
    x = random.randint(20, WIDTH - 20)
    y = 0
    food = canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="brown", outline="")
    food_list.append({"id": food, "x": x, "y": y})

root.bind("<space>", drop_food)

def animate():
    for fish in fish_list:

        # separace ryb
        for other in fish_list:
            if other is fish:
                continue

            dx = fish["x"] - other["x"]
            dy = fish["y"] - other["y"]
            dist = math.hypot(dx, dy)

            if 0 < dist < MIN_FISH_DISTANCE:
                fish["vx"] += (dx / dist) * REPULSION_STRENGTH
                fish["vy"] += (dy / dist) * REPULSION_STRENGTH

        # přitahování k jídlu
        if food_list:
            food = food_list[0]
            dx = food["x"] - fish["x"]
            dy = food["y"] - fish["y"]
            dist = math.hypot(dx, dy)

            if dist != 0:
                fish["vx"] += (dx / dist) * FOOD_ATTRACTION
                fish["vy"] += (dy / dist) * FOOD_ATTRACTION

        # omezení rychlosti
        speed = math.hypot(fish["vx"], fish["vy"])
        if speed > FISH_SPEED:
            fish["vx"] = (fish["vx"] / speed) * FISH_SPEED
            fish["vy"] = (fish["vy"] / speed) * FISH_SPEED

        fish["x"] += fish["vx"]
        fish["y"] += fish["vy"]

        # 🧱 WALL COLLISION + TURNING
        if fish["x"] <= 25 or fish["x"] >= WIDTH - 25:
            fish["vx"] *= -1
            flip_fish(fish)

        if fish["y"] <= 12 or fish["y"] >= HEIGHT - 12:
            fish["vy"] *= -1

        for part in fish["parts"]:
            canvas.move(part, fish["vx"], fish["vy"])

    # bublinky
    for bubble in bubble_list:
        canvas.move(bubble["id"], 0, -bubble["speed"])
        if canvas.coords(bubble["id"])[3] < 0:
            x = random.randint(20, WIDTH - 20)
            canvas.coords(bubble["id"], x - 4, HEIGHT - 4, x + 4, HEIGHT + 4)

    # jídlo
    for food in food_list[:]:
        food["y"] += FOOD_SPEED
        canvas.move(food["id"], 0, FOOD_SPEED)

        for fish in fish_list:
            if math.hypot(food["x"] - fish["x"], food["y"] - fish["y"]) < 20:
                canvas.delete(food["id"])
                food_list.remove(food)
                break

        if food["y"] > HEIGHT - SAND_HEIGHT:
            canvas.delete(food["id"])
            food_list.remove(food)

    root.after(30, animate)

animate()
root.mainloop()
