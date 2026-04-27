from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any

# Prefer a GUI-capable MuJoCo path for live rendering.
# This is different from lerobot-eval, which goes through LeRobot's offscreen
# LIBERO wrapper and typically renders frames for saved videos instead of a
# persistent live window.
os.environ.setdefault("MUJOCO_GL", "glfw")

import numpy as np
import torch
from libero.libero.envs.env_wrapper import ControlEnv
from libero.libero import get_libero_path

from lerobot.configs.policies import PreTrainedConfig
from lerobot.envs.factory import make_env_config, make_env_pre_post_processors
from lerobot.envs.libero import LiberoEnv as BaseLiberoEnv
from lerobot.envs.libero import _get_suite
from lerobot.envs.utils import preprocess_observation
from lerobot.policies.factory import make_pre_post_processors
from lerobot.utils.constants import ACTION

from load_smolvla import import_policy_class


class LiveLiberoEnv(BaseLiberoEnv):
    """LIBERO env that keeps the same LeRobot observation format but enables a live viewer."""

    def __init__(self, *args, render_camera: str = "frontview", **kwargs):
        self.render_camera_name = render_camera
        self._matplotlib_viewer = None
        self._matplotlib_image = None
        self._viewer_warning_printed = False
        super().__init__(*args, **kwargs)

    def _make_envs_task(self, task_suite: Any, task_id: int = 0):
        task = task_suite.get_task(task_id)
        self.task = task.name
        self.task_description = task.language
        task_bddl_file = os.path.join(get_libero_path("bddl_files"), task.problem_folder, task.bddl_file)

        env_args = {
            "bddl_file_name": task_bddl_file,
            "camera_heights": self.observation_height,
            "camera_widths": self.observation_width,
            "camera_names": ["agentview", "robot0_eye_in_hand"],
            "render_camera": self.render_camera_name,
            "has_renderer": True,
            "has_offscreen_renderer": True,
        }
        env = ControlEnv(**env_args)
        env.reset()
        return env

    def render_live(self) -> None:
        """Try the native robosuite/OpenCV viewer first, then fall back to matplotlib."""
        try:
            inner_env = self._env.env
            if hasattr(inner_env, "render"):
                inner_env.render()
                return
        except Exception as exc:
            if not self._viewer_warning_printed:
                print(f"[WARN] Native robosuite viewer failed, falling back to matplotlib: {exc}")
                self._viewer_warning_printed = True

        frame = self.render()
        self._render_with_matplotlib(frame)

    def _render_with_matplotlib(self, frame: np.ndarray) -> None:
        try:
            import matplotlib.pyplot as plt
        except Exception as exc:
            if not self._viewer_warning_printed:
                print(f"[WARN] Matplotlib fallback is unavailable: {exc}")
                self._viewer_warning_printed = True
            return

        if self._matplotlib_viewer is None:
            plt.ion()
            figure, axes = plt.subplots(figsize=(8, 6))
            axes.set_title("LIBERO live viewer")
            axes.axis("off")
            self._matplotlib_viewer = figure
            self._matplotlib_image = axes.imshow(frame)
        else:
            self._matplotlib_image.set_data(frame)

        self._matplotlib_viewer.canvas.draw_idle()
        self._matplotlib_viewer.canvas.flush_events()
        plt.pause(0.001)

    def close(self):
        try:
            super().close()
        finally:
            if self._matplotlib_viewer is not None:
                try:
                    import matplotlib.pyplot as plt

                    plt.close(self._matplotlib_viewer)
                except Exception:
                    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a single live-view LIBERO episode with a SmolVLA checkpoint."
    )
    parser.add_argument("--policy-path", default="HuggingFaceVLA/smolvla_libero")
    parser.add_argument("--task-suite", default="libero_object")
    parser.add_argument("--task-id", type=int, default=0)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--camera-name", default="agentview_image,robot0_eye_in_hand_image")
    parser.add_argument("--observation-width", type=int, default=360)
    parser.add_argument("--observation-height", type=int, default=360)
    parser.add_argument("--control-mode", default="relative", choices=["relative", "absolute"])
    parser.add_argument("--sleep", type=float, default=0.0, help="Optional pause after each rendered step.")
    parser.add_argument("--max-steps", type=int, default=None, help="Optional cap for quick testing.")
    parser.add_argument("--seed", type=int, default=1000)
    return parser.parse_args()


def load_policy(policy_path: str, device: str):
    policy_cfg = PreTrainedConfig.from_pretrained(policy_path)
    policy_cfg.device = device

    policy_class = import_policy_class()
    policy = policy_class.from_pretrained(policy_path, config=policy_cfg)

    preprocessor, postprocessor = make_pre_post_processors(policy.config, pretrained_path=policy_path)
    return policy, preprocessor, postprocessor


def make_env_processors(task_suite: str, task_id: int, camera_name: str, width: int, height: int, control_mode: str, policy_cfg):
    env_cfg = make_env_config(
        "libero",
        task=task_suite,
        task_ids=[task_id],
        render_mode="human",
        obs_type="pixels_agent_pos",
        camera_name=camera_name,
        observation_width=width,
        observation_height=height,
        control_mode=control_mode,
        max_parallel_tasks=1,
    )
    return make_env_pre_post_processors(env_cfg, policy_cfg)


def prepare_observation(observation: dict[str, Any], task_instruction: str, env_preprocessor, preprocessor):
    batch = preprocess_observation(observation)
    robot_state_key = "observation.robot_state"
    if robot_state_key in batch:
        batch[robot_state_key] = add_batch_dim_to_nested_tensors(batch[robot_state_key])
    batch["task"] = [task_instruction]
    batch = env_preprocessor(batch)
    batch = preprocessor(batch)
    return batch


def add_batch_dim_to_nested_tensors(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: add_batch_dim_to_nested_tensors(subvalue) for key, subvalue in value.items()}
    if isinstance(value, torch.Tensor) and value.ndim >= 1:
        return value.unsqueeze(0)
    return value


def main() -> int:
    args = parse_args()

    suite = _get_suite(args.task_suite)
    if args.task_id < 0 or args.task_id >= len(suite.tasks):
        raise ValueError(f"task_id {args.task_id} is out of range for suite '{args.task_suite}'.")

    env = LiveLiberoEnv(
        task_suite=suite,
        task_id=args.task_id,
        task_suite_name=args.task_suite,
        obs_type="pixels_agent_pos",
        render_mode="human",
        camera_name=args.camera_name,
        observation_width=args.observation_width,
        observation_height=args.observation_height,
        init_states=True,
        episode_index=0,
        n_envs=1,
        control_mode=args.control_mode,
    )

    try:
        print("Starting live LIBERO viewer episode")
        print(f"Policy checkpoint: {args.policy_path}")
        print(f"Task suite: {args.task_suite}")
        print(f"Task id: {args.task_id}")
        print(f"Language instruction: {env.task_description}")
        print(f"Device: {args.device}")
        print(f"MUJOCO_GL: {os.environ.get('MUJOCO_GL')}")

        policy, preprocessor, postprocessor = load_policy(args.policy_path, args.device)
        env_preprocessor, env_postprocessor = make_env_processors(
            args.task_suite,
            args.task_id,
            args.camera_name,
            args.observation_width,
            args.observation_height,
            args.control_mode,
            policy.config,
        )

        observation, info = env.reset(seed=args.seed)
        policy.reset()
        env.render_live()

        max_steps = args.max_steps or env._max_episode_steps
        print(f"Running one episode for up to {max_steps} steps...")

        for step_idx in range(max_steps):
            batch = prepare_observation(
                observation,
                env.task_description,
                env_preprocessor,
                preprocessor,
            )

            with torch.inference_mode():
                action = policy.select_action(batch)

            action = postprocessor(action)
            action_transition = env_postprocessor({ACTION: action})
            action_np = action_transition[ACTION].detach().to("cpu").numpy()
            action_np = np.asarray(action_np[0], dtype=np.float32)

            observation, reward, terminated, truncated, info = env.step(action_np)
            env.render_live()

            print(
                f"step={step_idx + 1:03d} reward={float(reward):.4f} "
                f"success={bool(info.get('is_success', False))} "
                f"terminated={terminated} truncated={truncated}"
            )

            if args.sleep > 0:
                time.sleep(args.sleep)

            if terminated or truncated:
                break

        final_success = bool(info.get("is_success", False))
        print(f"Episode finished. success={final_success}")
        return 0
    finally:
        env.close()


if __name__ == "__main__":
    raise SystemExit(main())
