import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Anna"
    
    def _get_turn_options(self, vx, vy):
        # Determine turn options based on current velocity
        # When hitting a wall, turn perpendicular to current direction
        
        if vx > 0:  # Moving right
            return [5, 3, 8, 6, 2, 0]  # Try down, up, then diagonals
        elif vx < 0:  # Moving left
            return [5, 3, 2, 0, 8, 6]  # Try down, up, then diagonals
        elif vy > 0:  # Moving down
            return [7, 1, 8, 2, 6, 0]  # Try right, left, then diagonals
        elif vy < 0:  # Moving up
            return [7, 1, 6, 0, 8, 2]  # Try right, left, then diagonals
        else:  # No velocity (stopped)
            return [7, 5, 8, 1, 3, 6, 2, 0]  # Try all directions

    def PickMove(self, auto, world, targets, validity):
        # If no possible moves at all
        if targets is None or len(targets) == 0:
            return None
        
        # Check if car has velocity
        has_velocity = auto.vel.vx != 0 or auto.vel.vy != 0
        
        if has_velocity:
            # Try to maintain current velocity (forward) - index 4
            forward_index = 4
            if forward_index < len(targets):
                if validity is None or (forward_index < len(validity) and validity[forward_index]):
                    return targets[forward_index]
            
            # Forward move is invalid - we hit a wall! Turn
            turn_options = self._get_turn_options(auto.vel.vx, auto.vel.vy)
            i = 0
            while i < len(turn_options):
                idx = turn_options[i]
                if idx < len(targets):
                    if validity is None or (idx < len(validity) and validity[idx]):
                        return targets[idx]
                i += 1
        else:
            # Car is stopped - start moving forward
            forward_index = 7  # Try accelerating right first
            if forward_index < len(targets):
                if validity is None or (forward_index < len(validity) and validity[forward_index]):
                    return targets[forward_index]
            
            # If right doesn't work, try other starting directions
            start_options = [5, 8, 1, 3, 6, 2, 0]
            i = 0
            while i < len(start_options):
                idx = start_options[i]
                if idx < len(targets):
                    if validity is None or (idx < len(validity) and validity[idx]):
                        return targets[idx]
                i += 1
        
        # Fallback: return first valid target
        if validity is not None:
            i = 0
            while i < len(validity):
                if validity[i] and i < len(targets):
                    return targets[i]
                i += 1
        
        return targets[0] if len(targets) > 0 else None
