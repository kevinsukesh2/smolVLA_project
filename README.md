# SmolVLA LIBERO Live Demo

This project runs a language-conditioned robot manipulation demo in simulation using:

- Hugging Face LeRobot
- SmolVLA
- LIBERO
- MuJoCo / robosuite live rendering

The setup is designed for:

- WSL2 Ubuntu
- Conda environment `lerobot`
- no ROS
- no Gazebo

## Main Scripts

- `scripts/live_libero_viewer.py`
  Runs one LIBERO task live with the SmolVLA checkpoint.
- `scripts/libero_task_gui.py`
  Opens a simple Tkinter GUI that lists LIBERO tasks and launches one selected task at a time.
- `scripts/load_smolvla.py`
  Loads SmolVLA and provides diagnostics for package/import issues.

## Running the Live Viewer Directly

```bash
conda activate lerobot
cd /path/to/smolVLA_project
export MUJOCO_GL=glfw
python scripts/live_libero_viewer.py --task-id 0
```

## Running the GUI Task Selector

```bash
conda activate lerobot
cd /path/to/smolVLA_project
export MUJOCO_GL=glfw
python scripts/libero_task_gui.py
```

If `tkinter` is missing in WSL Ubuntu, install it with:

```bash
sudo apt install python3-tk
```

## Why the GUI Runs One Task at a Time

LIBERO contains multiple tasks in each task suite, such as `libero_object`. Each task has:

- a `task_id`
- a language instruction
- a BDDL task definition file

The GUI only loads this task metadata first. It does not create all simulation environments at once. That keeps RAM usage lower and makes the launcher more stable on a laptop/WSL setup.

When you click `Run Selected Task`, the GUI launches a single live simulation for that one task.

## Proposal

The project proposal/status writeup is stored in:

- `README_proposal.md`
