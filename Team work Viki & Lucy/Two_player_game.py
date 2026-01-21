# Two_player_game
import tkinter as tk
import random
import math  # calculations of distance


# základní info (constants)
WIDTH = 700
HEIGHT = 450
BALL_RADIUS = 18
BALL_SPEED = 4
PLAYER_SPEED = 6
NUMBER_OF_ENEMIES = 8


# parent class - share behaviour
class MovingBall:
    def __init__(self, canvas, x, y, color, shape="circle"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.color = color
        self.alive = True
        self.shape = shape

        if self.shape == "circle":
            self.body = canvas.create_oval(
                self.x - BALL_RADIUS, self.y - BALL_RADIUS,
                self.x + BALL_RADIUS, self.y + BALL_RADIUS,
                fill=self.color, outline="black"
            )
        else:
            self.body = canvas.create_rectangle(
                self.x - BALL_RADIUS, self.y - BALL_RADIUS,
                self.x + BALL_RADIUS, self.y + BALL_RADIUS,
                fill=self.color, outline="black"
            )
        # updtaes th eposition 
    def move(self):
        if not self.alive:
            return

        self.x += self.dx
        self.y += self.dy

        if self.x <= BALL_RADIUS or self.x >= WIDTH - BALL_RADIUS:
            self.dx *= -1
        if self.y <= BALL_RADIUS or self.y >= HEIGHT - BALL_RADIUS:
            self.dy *= -1
         # -1 reverse direction 
            # keeep it in da place

        
        # keepinng it in the winddow
        self.x = max(BALL_RADIUS, min(WIDTH - BALL_RADIUS, self.x))
        self.y = max(BALL_RADIUS, min(HEIGHT - BALL_RADIUS, self.y))

        self.canvas.coords(
            self.body,
            self.x - BALL_RADIUS, self.y - BALL_RADIUS,
            self.x + BALL_RADIUS, self.y + BALL_RADIUS
        )

    def die(self): # dramatic death 
        self.alive = False
        self.canvas.itemconfig(self.body, fill="green")
        self.dx = 10
        self.dy = 0

        # slid out of the frame
    def slide_out(self):
        self.x += self.dx
        self.canvas.coords(
            self.body,
            self.x - BALL_RADIUS, self.y - BALL_RADIUS,
            self.x + BALL_RADIUS, self.y + BALL_RADIUS
        )
        if self.x > WIDTH + 50:
            self.canvas.delete(self.body)

# mentalita nepřítele
class EnemyBall(MovingBall):
    def __init__(self, canvas, x, y, color):
        super().__init__(canvas, x, y, color, "circle")
        self.dx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.dy = random.choice([-BALL_SPEED, BALL_SPEED])

# mentalita míčku   , class says what object has - variables + what it can do 
class PlayerBall(MovingBall):
    def __init__(self, canvas, x, y, color, shape, controls):
        super().__init__(canvas, x, y, color, shape)
        self.controls = controls

    # key press  # shared momevent style for both
    def handle_key_press(self, key):
        if key == self.controls.get("left"):    # changes velocity based on the pressed key
            self.dx = -PLAYER_SPEED             # its connected to the dictionary
        if key == self.controls.get("right"):
            self.dx = PLAYER_SPEED
        if key == self.controls.get("up"):
            self.dy = -PLAYER_SPEED
        if key == self.controls.get("down"):
            self.dy = PLAYER_SPEED
    def handle_key_release(self, key):
        if key in (self.controls["left"], self.controls["right"]):
            self.dx = 0
        if key in (self.controls["up"], self.controls["down"]):
            self.dy = 0


# collisions of the enemies
def check_collisions():
    for enemy in enemies:
        if enemy.alive:
            for player in players:
                distance = math.hypot(player.x - enemy.x, player.y - enemy.y)
                if distance < BALL_RADIUS * 2:  
                    enemy.die() # dies once touched by player
            # it calculates the distance between two balls centers and if they are touching death

def game_loop():
        #  move player, move enemy, check collision, again
    for player in players:
        player.move()

    for enemy in enemies:
        if enemy.alive:
            enemy.move()
        else:
            enemy.slide_out()

    check_collisions()
    root.after(16, game_loop)


def on_key_press(event):
    for player in players:
        player.handle_key_press(event.keysym)

def on_key_release(event):
    for player in players:
        player.handle_key_release(event.keysym)


# creates window/ canva
root = tk.Tk()
root.title("Ball Game DUO")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="pink")
canvas.pack()



# dictionary 
player1_controls = {"left": "Left", "right": "Right", "up": "Up", "down": "Down"}
player2_controls = {"left": "a", "right": "d", "up": "w", "down": "s"}


player1 = PlayerBall(canvas, WIDTH // 3, HEIGHT // 2, "blue", "circle", player1_controls ) # first object
player2 = PlayerBall(canvas, 2 * WIDTH // 3, HEIGHT // 2, "purple", "square", player2_controls) # second object
players = [player1, player2]
    # this creates a list of all players aka objects = all get treated equaly, in same loop

enemies = []
for _ in range(NUMBER_OF_ENEMIES): # spawning enemies on ranom places
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    enemies.append(EnemyBall(canvas, x, y, random.choice(["red", "black"])))


# calls keyboard # tkinter thing, it calls the function
root.bind("<KeyPress>", on_key_press) 
root.bind("<KeyRelease>", on_key_release)


game_loop() # update loop
root.mainloop() # keep the window open


