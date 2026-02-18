import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.script_api import AutoAuto
import torch
from neural.model import get_input_features, acceleration_to_index, index_to_acceleration, load_model


class Auto(AutoAuto):
    def __init__(self, model_path="neural/model.pth"):
        super().__init__()
        self.device = torch.device('cpu')
        self.model = load_model(model_path)
        if self.model is not None:
            self.model.eval()

    def GetName(self) -> str:
        return "Neural Auto"

    def PickMove(self, auto, world, allowed_moves):
        my_car = next((c for c in world.cars if c.id == auto.id), None)
        if my_car is None or self.model is None or len(allowed_moves) == 0:
            return None

        features = get_input_features(world, my_car)
        state_tensor = torch.tensor(features, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(state_tensor).squeeze(0)

        allowed_set = {(t.x, t.y) for t in allowed_moves}
        accel_to_target = {}
        for ax in range(-1, 2):
            for ay in range(-1, 2):
                tx = my_car.pos.x + my_car.vel.vx + ax
                ty = my_car.pos.y + my_car.vel.vy + ay
                if (tx, ty) in allowed_set:
                    idx = acceleration_to_index(ax, ay)
                    accel_to_target[idx] = (tx, ty)

        ranked = torch.argsort(logits, descending=True).tolist()
        for idx in ranked:
            if idx in accel_to_target:
                tx, ty = accel_to_target[idx]
                return next((t for t in allowed_moves if t.x == tx and t.y == ty), None)

        return allowed_moves[0]