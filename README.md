# Language-Conditioned Robot Manipulation with SmolVLA and LIBERO

Team Members:
- Kevin Sukesh, kevinsu2@buffalo.edu

---

## Project Objective

The goal of this project is to build and demonstrate a language-conditioned robot manipulation system in simulation using Hugging Face LeRobot, SmolVLA, and the LIBERO benchmark. The project focuses on getting a pretrained vision-language-action model to interpret natural-language commands and execute manipulation behaviors in a simulated environment, without using ROS or Gazebo.

The current implementation targets WSL2 Ubuntu with a Conda environment and uses LeRobot's simulation and evaluation tools together with LIBERO tasks. The main demonstration goal is to show that a SmolVLA-based policy can successfully run a manipulation task in simulation and that the system can be viewed both through saved evaluation videos and a live viewer script.

## Contributions

This project is interesting because it uses a learned robot policy rather than a traditional robotics pipeline based on manual perception, rule-based planning, or motion-planning frameworks. Instead of writing object-specific logic by hand, the project relies on a pretrained policy that maps images, robot state, and language instructions directly to actions.

The main contributions of the project so far are:

- Setting up a working LeRobot + SmolVLA + LIBERO simulation workflow on WSL2 Ubuntu.
- Verifying that `lerobot-eval` can run a LIBERO task successfully with the checkpoint `HuggingFaceVLA/smolvla_libero`.
- Building debugging and diagnostic scripts for SmolVLA loading.
- Identifying and patching a LeRobot 0.5.1 Python 3.12 GROOT import/dataclass bug that blocked both direct model loading and `lerobot-eval`.
- Building a custom live LIBERO viewer script so the simulation can be viewed during rollout instead of only after the evaluation video is saved.

## Project Plan

The project is being completed by incrementally building up the simulation stack, verifying each stage before moving to the next.

The plan is:

1. Set up a Linux-based simulation environment in WSL2 Ubuntu using Conda.
2. Install and verify PyTorch, Hugging Face tooling, LeRobot, SmolVLA support, and LIBERO support.
3. Confirm that the base SmolVLA model and a LIBERO-finetuned SmolVLA checkpoint can be loaded correctly.
4. Run a supported LIBERO task with `lerobot-eval` and confirm successful task completion.
5. Improve usability by adding a live viewer for rollout visualization.
6. Document current results, limitations, and possible future extensions such as custom tasks, custom language instructions, or fine-tuning on additional datasets.

Resources used for this project include:

- Hugging Face LeRobot documentation
- Hugging Face SmolVLA documentation and model pages
- LIBERO benchmark documentation and task assets
- robosuite and MuJoCo rendering stack
- Codex for implementation, debugging, and environment integration support

## Milestones/Schedule Checklist

- [x] Complete this proposal document. *Originally due April 28, 2026*
- [x] Set up WSL2 Ubuntu and Conda environment for LeRobot. *Completed*
- [x] Install and verify LeRobot, SmolVLA, PyTorch, and Hugging Face dependencies. *Completed*
- [x] Create setup and diagnostic scripts for environment verification. *Completed*
- [x] Load SmolVLA in Python and debug model import/runtime issues. *Completed*
- [x] Identify and patch the LeRobot 0.5.1 Python 3.12 GROOT import bug. *Completed*
- [x] Run `lerobot-eval` successfully on `HuggingFaceVLA/smolvla_libero` with `libero_object`, `task_id=0`. *Completed*
- [x] Create a live LIBERO viewer script for single-episode visualization. *Completed*
- [ ] Capture screenshots and/or short clips for the final demo. *Due before May 14, 2026*
- [ ] Summarize limitations, lessons learned, and next-step ideas. *Due before May 14, 2026*
- [ ] Create final presentation. *Due May 14, 2026*
- [ ] Provide system documentation (README.md). *Due May 15, 2026*

## Measures of Success

The project will be considered successful if the following outcomes are demonstrated:

- [x] A working WSL2 Ubuntu environment is configured for LeRobot + SmolVLA + LIBERO.
- [x] A SmolVLA-based policy can be loaded and evaluated in simulation.
- [x] A LIBERO task can be completed successfully using `lerobot-eval`.
- [x] A live simulation viewer can display the rollout during execution.
- [ ] A final demo clearly explains the system, environment, and results.
- [ ] A classmate or instructor can follow the repository documentation to understand what was built and how to run it.

Partial credit should be awarded if:

- the environment setup and policy loading work, even if the final demo is limited
- the evaluation pipeline runs successfully, even if customization and fine-tuning are incomplete
- the live viewer and debugging tools show clear technical effort and understanding of the system
