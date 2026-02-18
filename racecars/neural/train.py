import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import math
import argparse
import logging
import torch
import torch.optim as optim
from neural.model import RacecarNet, get_input_features, acceleration_to_index, index_to_acceleration, save_model, load_model
from simulation.game_state import GameState, create_cars_for_track
from simulation.track_generator import generate_track
from simulation.params import GameParams
from simulation.move_generator import get_move_options, get_allowed_targets, find_option_for_target
from simulation.script_api import build_world_state
from simulation.turn_logic import TurnLogic


class NeuralTrainer:
    def __init__(self, model_path=None):
        if model_path and os.path.exists(model_path):
            self.model = load_model(model_path)
        else:
            self.model = RacecarNet()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=2e-05)
        self.entropy_coef = 1e-3
        self.value_coef = 0.1
        self.logger = None
        
    def run_episode(self, params, max_steps=500, epsilon=0.1):
        seed = 12345 # random.randint(0, 1000000)
        track = generate_track(
            params.width, params.height, 1,
            params.track_width_mean, params.track_width_var, 
            params.turn_density, params.turn_sharpness,
            seed
        )
        
        cars = create_cars_for_track(track, 1)
        game_state = GameState(track, cars)
        
        states = []
        actions = []
        rewards = []
        action_masks = []
        
        step = 0
        prev_x = game_state.cars[0].pos.x
        
        while not game_state.finished and step < max_steps:
            options = get_move_options(game_state, 0)
            allowed_targets = get_allowed_targets(options)
            
            if len(allowed_targets) == 0:
                break
            
            world = build_world_state(game_state)
            my_car = world.cars[0]
            
            features = get_input_features(world, my_car)
            state_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)

            self.model.eval()
            with torch.no_grad():
                logits, _ = self.model(state_tensor)

            action_mask = self._create_action_mask(my_car, options)

            masked_logits = logits.clone()
            masked_logits[0, ~action_mask] = -1e9

            dist = torch.distributions.Categorical(logits=masked_logits)
            if random.random() < epsilon:
                valid_indices = action_mask.nonzero(as_tuple=True)[0]
                if len(valid_indices) > 0:
                    action_idx = int(valid_indices[random.randint(0, len(valid_indices) - 1)].item())
                else:
                    action_idx = 4
            else:
                action_idx = int(dist.sample().item())

            ax, ay = index_to_acceleration(action_idx)
            target = self._find_target_for_option(ax, ay, options)
            if target is None:
                target = allowed_targets[0]
            
            states.append(features)
            actions.append(action_idx)
            action_masks.append(action_mask.clone())
            
            option = find_option_for_target(options, target)
            penalty_before = game_state.cars[0].penalty_turns_left
            TurnLogic.apply_move(game_state, 0, option.acceleration)

            car = game_state.cars[0]
            crashed = (penalty_before == 0 and car.penalty_turns_left > 0)
            reward = self._calculate_reward(game_state, prev_x, crashed)
            rewards.append(reward)
            prev_x = car.pos.x
            
            step += 1
        
        if game_state.finished:
            bonus = 100.0 * (1 - step / max_steps)
            rewards[-1] += bonus
        elif step >= max_steps:
            rewards[-1] -= 50.0
        
        return {
            'states': states,
            'actions': actions,
            'action_masks': action_masks,
            'rewards': rewards,
            'finished': game_state.finished,
            'steps': step,
        }
    
    def _calculate_reward(self, game_state, prev_x, crashed=False):
        car = game_state.cars[0]

        if crashed:
            return -10.0

        if car.penalty_turns_left > 0:
            return -1.0

        current_x = car.pos.x
        dx = current_x - prev_x

        survival_bonus = 0.1
        progress = dx * 2.0

        return progress + survival_bonus
    
    def _distance_to_finish(self, game_state):
        car = game_state.cars[0]
        fl = game_state.track.finish_line
        dx = (fl.start.x + fl.end.x) / 2 - car.pos.x
        dy = (fl.start.y + fl.end.y) / 2 - car.pos.y
        return math.hypot(dx, dy)
    
    def _create_action_mask(self, car, options):
        mask = torch.zeros(9, dtype=torch.bool)
        stay_idx = acceleration_to_index(0, 0)
        valid_count = 0
        for opt in options:
            if opt.valid:
                idx = acceleration_to_index(opt.acceleration.vx, opt.acceleration.vy)
                mask[idx] = True
                valid_count += 1

        if valid_count > 1 and getattr(car, 'penalty_turns_left', 0) == 0:
            mask[stay_idx] = False

        if not mask.any():
            for opt in options:
                idx = acceleration_to_index(opt.acceleration.vx, opt.acceleration.vy)
                mask[idx] = True
        return mask

    def _find_target_for_option(self, ax, ay, options):
        for opt in options:
            if opt.acceleration.vx == ax and opt.acceleration.vy == ay:
                return opt.target
        return None
    
    
    def train_on_episodes(self, episodes_data):
        self.model.train()
        total_loss = 0.0
        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_entropy = 0.0
        total_adv_mean = 0.0
        total_adv_std = 0.0
        total_grad_norm = 0.0
        num_updates = 0

        for ep_data in episodes_data:
            rewards = ep_data['rewards']
            if not rewards:
                continue

            returns = []
            G = 0.0
            for r in reversed(rewards):
                G = r + G
                returns.insert(0, G)
            returns_raw = torch.tensor(returns, dtype=torch.float32)
            # clip extreme returns then normalize per-episode for stability
            returns_clipped = torch.clamp(returns_raw, -100.0, 100.0)
            if returns_clipped.numel() > 1:
                rmean = returns_clipped.mean()
                rstd = returns_clipped.std(unbiased=False)
                if rstd < 1e-6:
                    rstd = 1.0
                returns_norm = (returns_clipped - rmean) / (rstd + 1e-8)
            else:
                returns_norm = returns_clipped

            states = torch.tensor(ep_data['states'], dtype=torch.float32)
            actions = torch.tensor(ep_data['actions'], dtype=torch.long)
            masks = torch.stack(ep_data['action_masks']).to(dtype=torch.bool)

            logits, values = self.model(states)
            logits[~masks] = -1e9

            dist = torch.distributions.Categorical(logits=logits)
            logp = dist.log_prob(actions)
            entropy = dist.entropy()

            values = values.squeeze(-1)

            advantage = returns_norm - values.detach()
            adv_mean = float(advantage.mean().item()) if advantage.numel() > 0 else 0.0
            adv_std = float(advantage.std(unbiased=False).item()) if advantage.numel() > 1 else 0.0
            if advantage.numel() > 1:
                if adv_std < 1e-6:
                    adv_std = 1.0
                advantage = (advantage - adv_mean) / (adv_std + 1e-8)

            policy_loss = -(logp * advantage).mean()
            value_loss = torch.nn.functional.mse_loss(values, returns_norm)
            loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy.mean()

            self.optimizer.zero_grad()
            loss.backward()
            total_norm = 0.0
            for p in self.model.parameters():
                if p.grad is not None:
                    param_norm = p.grad.data.norm(2)
                    total_norm += float(param_norm.item()) ** 2
            total_norm = float(math.sqrt(total_norm))
            total_grad_norm += total_norm

            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 0.5)
            self.optimizer.step()

            total_loss += float(loss.item())
            total_policy_loss += float(policy_loss.item())
            total_value_loss += float(value_loss.item())
            total_entropy += float(entropy.mean().item())
            total_adv_mean += adv_mean
            total_adv_std += adv_std
            num_updates += 1

        if num_updates == 0:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

        return (
            total_loss / num_updates,
            total_policy_loss / num_updates,
            total_value_loss / num_updates,
            total_entropy / num_updates,
            total_adv_mean / num_updates,
            total_adv_std / num_updates,
            total_grad_norm / num_updates,
        )
    
    def train(self, num_epochs=100, episodes_per_epoch=20, save_path="neural/model.pth"):
        if self.logger is None:
            log_file = save_path.replace('.pth', '.log')
            self.logger = logging.getLogger(f'neural.train.{id(self)}')
            self.logger.setLevel(logging.INFO)
            fh = logging.FileHandler(log_file, mode='a')
            fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
            self.logger.addHandler(fh)
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(ch)

        self.logger.info(f"\nTraining for {num_epochs} epochs, {episodes_per_epoch} episodes each...")
        
        best_finish_rate = 0
        best_avg_steps = float('inf')
        
        for epoch in range(num_epochs):
            params = GameParams()
            epsilon = max(0.05, 0.25 * (1 - (epoch / num_epochs)))
            
            episodes_data = []
            finishes = 0
            total_steps = 0
            total_reward = 0
            
            for _ in range(episodes_per_epoch):
                ep_data = self.run_episode(params, epsilon=epsilon)
                episodes_data.append(ep_data)
                
                if ep_data['finished']:
                    finishes += 1
                total_steps += ep_data['steps']
                total_reward += sum(ep_data['rewards'])
            
            (avg_loss, avg_policy_loss, avg_value_loss, avg_entropy, avg_adv_mean, avg_adv_std, avg_grad_norm) = self.train_on_episodes(episodes_data)

            finish_rate = finishes / episodes_per_epoch
            avg_steps = total_steps / episodes_per_epoch
            avg_reward = total_reward / episodes_per_epoch

            self.logger.info(
                f"Epoch {epoch+1}/{num_epochs}: "
                f"Finish: {finish_rate:.0%}, "
                f"Steps: {avg_steps:.0f}, "
                f"Reward: {avg_reward:.1f}, "
                f"Loss: {avg_loss:.4f}, "
                f"Policy: {avg_policy_loss:.4f}, "
                f"Value: {avg_value_loss:.4f}, "
                f"Ent: {avg_entropy:.4f}, "
                f"AdvMean: {avg_adv_mean:.4f}, "
                f"AdvStd: {avg_adv_std:.4f}, "
                f"GNorm: {avg_grad_norm:.4f}"
            )
            
            if finish_rate > best_finish_rate or (finish_rate == best_finish_rate and avg_steps < best_avg_steps):
                best_finish_rate = finish_rate
                best_avg_steps = avg_steps
                save_model(self.model, save_path)
                self.logger.info(f"Saved (finish={finish_rate:.0%}, steps={avg_steps:.0f})")
            
            if (epoch + 1) % 100 == 0:
                checkpoint_path = save_path.replace('.pth', f'_ep{epoch+1}.pth')
                save_model(self.model, checkpoint_path)
                self.logger.info(f"Checkpoint saved: {checkpoint_path}")
        
        save_model(self.model, save_path)
        self.logger.info(f"Finished Best: {best_finish_rate:.0%} finish rate")


def main():
    parser = argparse.ArgumentParser(description='Train neural network for racecar')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--episodes', type=int, default=20)
    parser.add_argument('--load', type=str, default=None)
    parser.add_argument('--save', type=str, default='neural/model.pth')
    
    args = parser.parse_args()
    
    trainer = NeuralTrainer(model_path=args.load)
    trainer.train(num_epochs=args.epochs, episodes_per_epoch=args.episodes, save_path=args.save)


if __name__ == '__main__':
    main()