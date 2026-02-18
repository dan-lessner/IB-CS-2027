import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        # Make the car move forward
        if targets is None:
            return None
        if len(targets) == 0:
            return None
        
        # Check if car has velocity - if zero, accelerate forward
        has_velocity = auto.vel.vx != 0 or auto.vel.vy != 0
        
        if has_velocity:
            # Maintain current velocity (ax=0, ay=0) - index 4
            forward_index = 4
        else:
            # Car is stopped - accelerate forward (ax=1, ay=0) - index 7
            # Or try (ax=0, ay=1) - index 5, or (ax=1, ay=1) - index 8
            forward_index = 7  # Try accelerating in x direction first
        
        # Try the preferred forward move
        if forward_index < len(targets):
            if validity is None or (forward_index < len(validity) and validity[forward_index]):
                return targets[forward_index]
        
        # If preferred move not valid, try other forward options
        forward_options = [4, 7, 5, 8, 6]  # maintain, x+, y+, xy+, x+y-
        i = 0
        while i < len(forward_options):
            idx = forward_options[i]
            if idx < len(targets):
                if validity is None or (idx < len(validity) and validity[idx]):
                    return targets[idx]
            i += 1
        
        # Fallback: return first valid target or first target
        if validity is not None:
            i = 0
            while i < len(validity):
                if validity[i] and i < len(targets):
                    return targets[i]
                i += 1
        
        return targets[0] if len(targets) > 0 else None
