import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        if targets is None or len(targets) == 0:
            return None

        best_target = None
        best_score = -999999

        # bias směrem doprava (k cíli)
        right_bias = {
            7: 3,   # silně doprava
            8: 2,   # diagonála doprava
            5: 1,   # trochu dopředu
            4: 0.5, # drzi směr
            6: 1,
            3: -1,  # doleva = špatně
            1: -2,
            0: -2,
            2: -1
        }

        i = 0
        while i < len(targets):
            if validity is None or (i < len(validity) and validity[i]):
                score = 0

                #jdi doprava kokote
                if i in right_bias:
                    score += right_bias[i]

                # random aby se to kurva uz nesekalo
                score += random.random() * 0.2

                if score > best_score:
                    best_score = score
                    best_target = targets[i]

            i += 1

        if best_target is not None:
            return best_target

        # fallback
        if validity is not None:
            i = 0
            while i < len(validity):
                if validity[i] and i < len(targets):
                    return targets[i]
                i += 1

        return targets[0]
