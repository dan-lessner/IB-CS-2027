import tkinter as tk
import random
import math

# Initial setup
WIDTH, HEIGHT = 2560, 1664
R = 30
FRICTION = 0.9
DT = 10
POCKET_R = 68

class Ball:
    def __init__(self, canvas, x, y, color, number):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.is_aiming = False
        self.aim_line = None

        # Create ball
        self.id = canvas.create_oval(x-R, y-R, x+R, y+R, fill=color, outline="black")
        
        # --- CHANGED: Added Number Text ---
        t_color = "white" if color == "black" else "black"
        self.text_id = canvas.create_text(x, y, text=str(number), fill=t_color, font=("Arial", 10, "bold"))

        # Bind events to both oval and text
        for item in (self.id, self.text_id):
            canvas.tag_bind(item, "<Button-1>", self.start_aim)
            canvas.tag_bind(item, "<B1-Motion>", self.update_aim)
            canvas.tag_bind(item, "<ButtonRelease-1>", self.shoot)

    def start_aim(self, event):
        self.is_aiming = True

    def update_aim(self, event):
        if not self.is_aiming: return
        if self.aim_line: self.canvas.delete(self.aim_line)
        self.aim_line = self.canvas.create_line(self.x, self.y, event.x, event.y, fill="white", width=2)

    def shoot(self, event):
        if not self.is_aiming: return
        dx, dy = self.x - event.x, self.y - event.y
        distance = math.hypot(dx, dy)
        power = min(distance / 10, 20)
        angle = math.atan2(dy, dx)
        self.vx, self.vy = math.cos(angle) * power, math.sin(angle) * power
        self.is_aiming = False
        if self.aim_line:
            self.canvas.delete(self.aim_line)
            self.aim_line = None

    def move(self):
        self.x += self.vx * DT
        self.y += self.vy * DT

        # Wall collisions (Mantinels) using the actual window size
        if self.x - R < 0:
            self.x = R
            self.vx = -self.vx
        elif self.x + R > WIDTH:
            self.x = WIDTH - R
            self.vx = -self.vx

        if self.y - R < 0:
            self.y = R
            self.vy = -self.vy
        elif self.y + R > HEIGHT:
            self.y = HEIGHT - R
            self.vy = -self.vy

        self.vx *= FRICTION
        self.vy *= FRICTION

        if abs(self.vx) < 0.05: self.vx = 0
        if abs(self.vy) < 0.05: self.vy = 0

        self.canvas.coords(self.id, self.x-R, self.y-R, self.x+R, self.y+R)
        # --- CHANGED: Update text position ---
        self.canvas.coords(self.text_id, self.x, self.y)
        self.check_pocket()

    def check_pocket(self):
        for px, py in POCKETS:
            if math.hypot(self.x - px, self.y - py) < POCKET_R:
                self.canvas.delete(self.id)
                self.canvas.delete(self.text_id)
                if self in balls: balls.remove(self)
                return

    def collide_with(self, other):
        dx, dy = other.x - self.x, other.y - self.y
        dist = math.hypot(dx, dy)
        if 0 < dist <= 2*R:
            nx, ny = dx / dist, dy / dist
            p1 = self.vx * nx + self.vy * ny
            p2 = other.vx * nx + other.vy * ny
            self.vx += (p2 - p1) * nx
            self.vy += (p2 - p1) * ny
            other.vx += (p1 - p2) * nx
            other.vy += (p1 - p2) * ny
            overlap = 2*R - dist
            self.x -= nx * overlap / 2
            self.y -= ny * overlap / 2
            other.x += nx * overlap / 2
            other.y += ny * overlap / 2

def tick():
    for b in balls[:]: b.move()
    for i in range(len(balls)):
        for j in range(i+1, len(balls)):
            balls[i].collide_with(balls[j])
    root.after(16, tick)

root = tk.Tk()
root.title("Pool Game")
root.state('zoomed')

# --- CHANGED: c is the single canvas ---
c = tk.Canvas(root, bg="darkgreen", highlightthickness=0)
c.pack(fill="both", expand=True)

root.update()
WIDTH = c.winfo_width()
HEIGHT = c.winfo_height()

# --- FIXED: Pocket coordinates with closing bracket ---
POCKETS = [
    (0, 0), (WIDTH/2, 0), (WIDTH, 0),
    (0, HEIGHT/2), (WIDTH, HEIGHT/2),
    (0, HEIGHT), (WIDTH/2, HEIGHT), (WIDTH, HEIGHT)
]

for px, py in POCKETS:
    c.create_oval(px-POCKET_R, py-POCKET_R, px+POCKET_R, py+POCKET_R, fill="black", outline="gray")

# Balls with numbers
balls = [
    Ball(c, WIDTH * 0.75, 535, "white", ""),
    Ball(c, WIDTH * 0.25, 535, "red", "1"),      
    Ball(c, WIDTH * 0.25 - 52, 505, "yellow", "2"),   
    Ball(c, WIDTH * 0.25 - 52, 565, "blue", "3"),
    Ball(c, WIDTH * 0.25 - 104, 475, "pink", "4"),     
    Ball(c, WIDTH * 0.25 - 104, 535, "black", "8"),    
    Ball(c, WIDTH * 0.25 - 104, 595, "orange", "5"),
    Ball(c, WIDTH * 0.25 - 156, 445, "cyan", "6"),    
    Ball(c, WIDTH * 0.25 - 156, 505, "purple", "7"),
    Ball(c, WIDTH * 0.25 - 156, 565, "gray", "9"),
    Ball(c, WIDTH * 0.25 - 156, 625, "magenta", "10")
]

tick()
root.mainloop()