# Live Robot Manipulation in Simulation Using SmolVLA, LeRobot, and LIBERO

Team Member:
- Kevin Sukesh, kevinsu2@buffalo.edu

---

## Motivation / Overview of the Project

The goal of this project is to create a live robot manipulation simulation using a Vision-Language-Action model called **SmolVLA**. The robot performs a manipulation task in simulation using camera observations, robot state information, and a natural-language task instruction.

I chose this project because I wanted to explore modern robot learning and language-conditioned robot control. My original idea was to make a robot pick and place objects using natural-language prompts. A traditional robotics approach would usually require separate modules for object detection, coordinate estimation, motion planning, and gripper control. Instead, this project uses a learned robot policy that directly maps observations and instructions to robot actions.

Extra features added:
- Added a GUI task selector to list all LIBERO tasks and choose one from a menu.
- you can run and compare multiple LIBERO task IDs.
- Created a custom LIBERO task suite, for example picking a yellow mug and placing it into a basket. Find this in "kevins custom suite" in the drop down in the GUI and select task 0. 

At a high level, the system works like this:

```text
Natural-language task instruction
+ camera observations
+ robot state
        ↓
SmolVLA
        ↓
robot actions
        ↓
simulated robot movement
```
The project runs by using Hugging Face LeRobot as the main framework that connects the robot policy to the simulation environment. LIBERO provides the manipulation task, including the robot scene, objects, task instruction, and success condition. Underneath LIBERO, MuJoCo / robosuite simulate the actual physics: robot arm motion, object movement, collisions, gripper behavior, and camera views. SmolVLA is the Vision-Language-Action model that receives the LIBERO camera observations, robot state, and language instruction, then predicts the robot actions. LeRobot passes those actions back into the LIBERO environment, MuJoCo/robosuite executes them physically in simulation, and the live viewer shows the robot completing the task step by step.

This project should be useful to students interested in robot learning, language-conditioned robotics, simulation-based robot development, and alternatives to traditional hand-coded robotics pipelines such as ROS/Gazebo/MoveIt/OpenCV.

The project uses:

- **WSL2 Ubuntu** for the Linux environment.
- **Conda / Miniforge** for environment management.
- **Python** for scripting.
- **PyTorch + CUDA** for running the deep learning model on the GPU.
- **Hugging Face LeRobot** as the robotics learning framework.
- **SmolVLA** as the Vision-Language-Action model.
- **LIBERO** as the robot manipulation simulation benchmark.
- **MuJoCo / robosuite** as the physics simulation layer.
- **A custom live viewer script** to show the robot moving live in simulation.

---

## Demonstration

**YouTube demo link:** TODO - add YouTube link here

The project can also run a headless evaluation that saves an `.mp4` video afterward. However, the main demonstration uses the custom live viewer script so that the robot can be seen moving live on screen.

---

## Installation Instructions

These instructions are written for a third party who wants to recreate the project.

### Assumptions

- The recommended setup is **Windows 11 with WSL2 Ubuntu**, or native Ubuntu/Linux.
- Commands should be run in WSL/Linux, **not Windows PowerShell**.
- An NVIDIA GPU with CUDA support is recommended for better performance.
- Conda/Miniforge is used to manage the Python environment.
- The project was tested in WSL2 Ubuntu.

---

### 1. Clone the Repository

```bash
git clone https://github.com/kevinsukesh2/smolVLA_project.git
cd smolVLA_project
```

---

### 2. Install Miniforge / Conda

If Conda is already installed, this step can be skipped.

```bash
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
source ~/.bashrc
conda --version
```

If `conda --version` prints a version number, Conda is available.

---

### 3. Create and Activate the Environment

```bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

---

### 4. Run the Setup Script

```bash
bash setup.sh
```

The setup script installs or prepares the LeRobot/SmolVLA-related dependencies used by the project.

---

### 5. Install Additional LIBERO / Rendering Dependencies if Needed

Some systems may need extra graphics and build dependencies for MuJoCo, robosuite, and LIBERO rendering.

```bash
sudo apt update
sudo apt install -y cmake build-essential ninja-build pkg-config \
  libegl1 libegl1-mesa-dev libgl1-mesa-dev libosmesa6-dev mesa-utils \
  x11-apps
```

---

### 6. Verify WSL GUI Works

```bash
echo $DISPLAY
xeyes
```

If an `xeyes` window opens, WSL GUI support is working. Close the window or press `Ctrl+C` in the terminal when finished.

---

### 7. Verify the Python Environment

```bash
python scripts/test_install.py
```

Expected result:

- Python version prints.
- PyTorch imports successfully.
- CUDA availability prints.
- LeRobot imports successfully.

---

### 8. Verify SmolVLA Loads

```bash
python scripts/load_smolvla.py
```

This downloads and loads the SmolVLA model. The first run may take time because model files are downloaded from Hugging Face.

---

### 9. Patch LeRobot Import Issue if Needed

The repository includes `scripts/patch_lerobot_groot_import.py` for reproducibility. Some LeRobot/Python 3.12 setups may hit a GROOT import issue related to a `backbone_cfg` dataclass error.

If SmolVLA or `lerobot-eval` fails with a `backbone_cfg` dataclass error, run:

```bash
python scripts/patch_lerobot_groot_import.py "$(python -c 'import site; print(site.getsitepackages()[0])')"
```

This script makes backups before patching. Skip this step if the model and evaluation already run correctly.

---

## How to Run the Code

Use these steps on a fresh WSL2 Ubuntu setup.

## 1. Clone the repo
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd "smolVLA_project"
```

## 2. Open WSL Ubuntu and create the environment
```bash
sudo apt update
sudo apt install -y python3-tk ffmpeg build-essential cmake git pkg-config python3-dev
source /home/kevin/miniforge3/etc/profile.d/conda.sh
conda create -n lerobot python=3.12 -y
conda activate lerobot
```

## 3. Install dependencies
```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install num2words
python -m pip install "lerobot[smolvla,libero] @ git+https://github.com/huggingface/lerobot.git"
```

## 4. Enable GUI rendering
```bash
export MUJOCO_GL=glfw
```

## 5. Run the project

### GUI task selector
```bash
python scripts/libero_task_gui.py
```

### Or run the built-in live demo directly
```bash
python scripts/live_libero_viewer.py --task-id 0
```

### Or run the custom task
```bash
python scripts/live_libero_viewer.py --task-suite Kevins_custom_suite --task-id 0
```

## 6. Optional checks
```bash
python scripts/test_install.py
python scripts/load_smolvla.py
```

If `tkinter` is missing:
```bash
sudo apt install python3-tk
```
---

### 5. File Overview

- `scripts/test_install.py`  
  Checks Python, PyTorch, CUDA, and LeRobot.

- `scripts/load_smolvla.py`  
  Loads SmolVLA and verifies that the model can run.

- `scripts/live_libero_viewer.py`  
  Main live demo script. It runs one LIBERO task and renders the robot moving live.

- `scripts/run_libero_eval.sh`  
  Helper script for the headless evaluation command.

- `scripts/patch_lerobot_groot_import.py`  
  Helper patch script for a possible LeRobot import issue.

- `setup.sh`  
  Setup helper for project dependencies.

- `requirements.txt`  
  Dependency reference file.

---

## References

### Helpful References

- Hugging Face LeRobot GitHub: https://github.com/huggingface/lerobot
- LeRobot documentation: https://huggingface.co/docs/lerobot
- SmolVLA blog: https://huggingface.co/blog/smolvla
- SmolVLA base model: https://huggingface.co/lerobot/smolvla_base
- LIBERO project/documentation: https://lifelong-robot-learning.github.io/LIBERO/html/index.html
- LIBERO GitHub: https://github.com/Lifelong-Robot-Learning/LIBERO
- MuJoCo: https://mujoco.org/
- robosuite: https://robosuite.ai/
- PyTorch: https://pytorch.org/
- Miniforge: https://github.com/conda-forge/miniforge

### Less Helpful / Not Used as Final Direction

- ROS 2 / Gazebo tutorials were helpful for understanding classical simulation workflows, but this final project did not use ROS or Gazebo.
- General OpenCV pick-and-place tutorials were useful conceptually, but the final system used a learned Vision-Language-Action policy rather than manual object detection and coordinate conversion.
- Some generic robot simulation resources were less directly useful because this project used the LeRobot/LIBERO ecosystem.

---

## Future Work

If I had more time, I would improve the project in the following ways:

### New Features

- Fine-tune SmolVLA on a custom pick-and-place dataset.
- Test on native Linux or a stronger GPU system.
- Explore real robot deployment using a robot supported by LeRobot.

### Known Issues / Limitations

- The first model run can take time because Hugging Face model files are downloaded.
- Running all LIBERO tasks at once can use too much memory, so the project runs one task at a time.
- The current demo uses predefined LIBERO tasks.
- Arbitrary user prompts are not yet supported.
- A new custom task may require new BDDL files, initial states, assets, and possibly fine-tuning.
- The existing pretrained/fine-tuned SmolVLA checkpoint works best on LIBERO-style tasks and may not generalize to completely new custom tasks without fine-tuning.
- Live rendering depends on WSL GUI / graphics support. If live rendering fails, users can use headless evaluation to generate videos.

### Suggestions for Future Fixes

- If memory usage is too high, run only one task at a time using `--task-id` and avoid loading all LIBERO tasks at once.
- If live rendering fails, first test WSL GUI using `xeyes`, then use `MUJOCO_GL=glfw` for the live viewer.
- If model loading fails due to LeRobot import problems, try the included patch script and check the installed LeRobot version.
- If a custom task does not work, inspect the BDDL task definition, object assets, initial states, and whether the model needs task-specific fine-tuning.

---

## Final Summary

This project demonstrates a working live simulation where SmolVLA controls a robot from camera observations, robot state, and a language instruction. It shows how Vision-Language-Action models can be used for robot manipulation without manually coding every perception, planning, and control step. Custom task was created and the robot simulation seems to go towards it but has ultimately been unsuccessful during testing but this can be improved with finetuning.
