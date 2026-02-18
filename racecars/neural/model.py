import torch
import torch.nn as nn
import math
import os


class RacecarNet(nn.Module):
    def __init__(self, input_size=16, hidden_size=128):
        super().__init__()
        self.input_size = input_size
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 9),
        )
        self.value_head = nn.Linear(hidden_size, 1)

    def forward(self, x):
        features = x
        logits = self.net(features)
        h = features
        for layer in list(self.net)[:-1]:
            h = layer(h)
        value = self.value_head(h).squeeze(-1)
        return logits, value


def get_input_features(world, car):
    tw, th = len(world.road), len(world.road[0]) if world.road else 0
    scale = max(tw, th, 1)
    
    finish_x = sum(v.x for v in world.finish_vertices) / len(world.finish_vertices)
    finish_y = sum(v.y for v in world.finish_vertices) / len(world.finish_vertices)
    dx, dy = finish_x - car.pos.x, finish_y - car.pos.y
    
    speed = math.hypot(car.vel.vx, car.vel.vy)
    dist = math.hypot(dx, dy)
    alignment = (car.vel.vx * dx + car.vel.vy * dy) / (speed * dist) if speed > 0 and dist > 0 else 0
    
    return [
        car.pos.x / scale, car.pos.y / scale,
        car.vel.vx, car.vel.vy, speed,
        dx / scale, dy / scale,
        *get_raycast(world.road, car.pos.x, car.pos.y, tw, th),
        alignment
    ]


DIRECTIONS = [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]

def get_raycast(road, px, py, tw, th, max_dist=20):
    def on_road(x, y):
        for cx, cy in [(int(x), int(y)), (int(x)-1, int(y)), (int(x), int(y)-1), (int(x)-1, int(y)-1)]:
            if 0 <= cx < tw and 0 <= cy < th and road[cx][cy]:
                return True
        return False
    
    result = []
    for dx, dy in DIRECTIONS:
        dist = max_dist
        for step in range(1, max_dist + 1):
            if not on_road(px + dx * step, py + dy * step):
                dist = step
                break
        result.append(dist / max_dist)
    return result

def acceleration_to_index(ax, ay):
    return (ax + 1) * 3 + (ay + 1)

def index_to_acceleration(idx):
    ax = (idx // 3) - 1
    ay = (idx % 3) - 1
    return ax, ay

def save_model(model, filepath):
    dirpath = os.path.dirname(filepath) or '.'
    os.makedirs(dirpath, exist_ok=True)
    torch.save({'state_dict': model.state_dict(), 'input_size': model.input_size}, filepath)

def load_model(filepath):
    if not os.path.exists(filepath):
        return None
    data = torch.load(filepath, map_location='cpu')
    input_size = data.get('input_size', 16)
    model = RacecarNet(input_size=input_size)
    model.load_state_dict(data['state_dict'])
    return model
