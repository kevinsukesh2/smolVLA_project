# Project Plan

## Milestone 1: Environment setup

- Set up WSL2 Ubuntu with Conda.
- Create or reuse the `lerobot` environment.
- Install LeRobot with SmolVLA and LIBERO support.
- Verify `torch` and `lerobot` imports.

## Milestone 2: Load SmolVLA

- Load the base model `lerobot/smolvla_base`.
- Confirm that the model downloads and initializes correctly.
- Keep this step limited to inference-time loading only.

## Milestone 3: Run LIBERO simulation

- Prepare a simple `lerobot-eval` command for a LIBERO suite.
- Confirm that simulation dependencies work under WSL2 Ubuntu.
- Test a small evaluation run with a suitable checkpoint.

## Milestone 4: Demonstrate language-conditioned manipulation

- Use a natural-language instruction for a pick/place style task.
- Run the policy in simulation.
- Observe whether the checkpoint behavior matches the requested task.

## Milestone 5: Final report/demo video

- Capture the setup process and final simulation result.
- Summarize what worked, what needed fine-tuning, and next steps.
- Package the demo as a short report or video walkthrough.
