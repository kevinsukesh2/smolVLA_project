# SmolVLA Project

This project is a simple starter repo for a language-conditioned robot manipulation demo using Hugging Face LeRobot, SmolVLA, and a simulation benchmark such as LIBERO.

The goal is to stay beginner-friendly and simulation-focused:

- WSL2 Ubuntu
- Conda-based Python environment
- No ROS
- No Gazebo

## What this project demonstrates

LeRobot + SmolVLA uses a learned robot policy instead of a hand-written planning stack such as OpenCV pipelines, classical grasp heuristics, or MoveIt-based motion planning. In this setup, the policy learns to map observations and a natural-language instruction to robot actions.

That makes this project a good starting point for language-conditioned manipulation in simulation, where we can test ideas before worrying about real hardware.

## Repo layout

```text
smolVLA_project/
├── README.md
├── setup.sh
├── requirements.txt
├── scripts/
│   ├── test_install.py
│   ├── load_smolvla.py
│   └── run_libero_eval.sh
└── notes/
    └── project_plan.md
```

## WSL2 Ubuntu setup

1. Open Ubuntu inside WSL2.
2. Make sure Conda is installed and available in your shell.
3. Enter this project directory:

```bash
cd smolVLA_project
```

4. Run the setup script:

```bash
bash setup.sh
```

The script is written to use or create a Conda environment named `lerobot`.

## Python dependencies

`requirements.txt` is intentionally minimal and is mainly useful for quick checks and lightweight installs. The main setup path is `setup.sh`, because LeRobot's simulation and SmolVLA support are best installed with the proper extras.

## Verify the install

Activate the environment first if needed:

```bash
conda activate lerobot
```

Then run:

```bash
python scripts/test_install.py
```

This checks:

- Python version
- `torch` import
- CUDA availability
- `lerobot` import

## Load the SmolVLA base model

To verify model loading from Hugging Face without starting training:

```bash
python scripts/load_smolvla.py
```

This loads:

```text
lerobot/smolvla_base
```

If you want to print environment diagnostics without attempting the model load:

```bash
python scripts/load_smolvla.py --diagnose-only
```

If you want diagnostics first and then a load attempt:

```bash
python scripts/load_smolvla.py --diagnose
```

## SmolVLA import bug notes

In one tested environment:

- WSL2 Ubuntu
- Conda env `lerobot`
- Python `3.12.13`
- LeRobot `0.5.1`

the direct SmolVLA import failed before model loading because `lerobot.policies.__init__` eagerly imported unrelated policy modules, including GROOT. In that installed package, Python raised:

```text
TypeError: non-default argument 'backbone_cfg' follows default argument
```

That error came from the installed file:

```text
lerobot/policies/groot/groot_n1.py
```

not from the SmolVLA model file itself.

The same LeRobot `0.5.1` on Python `3.12` bug can also block `lerobot-eval`, even when you are evaluating a SmolVLA checkpoint, because the CLI imports `lerobot.configs.eval`, which imports `from lerobot import envs, policies`, and that eventually trips over the broken GROOT import path before evaluation starts.

The updated `scripts/load_smolvla.py` now:

- tries the standard SmolVLA import first
- detects the GROOT-side `backbone_cfg` dataclass failure
- falls back to a SmolVLA-only import path that bypasses the broken eager import
- prints diagnostics automatically if loading still fails

## Fix options if SmolVLA still fails

### Option 1: Update LeRobot from GitHub main

This is the best first fix when PyPI `0.5.1` is the broken version in your environment.

```bash
pip uninstall -y lerobot
pip install "lerobot[smolvla,libero] @ git+https://github.com/huggingface/lerobot.git"
python -m pip install num2words
```

### Option 2: Pin to a stable LeRobot version

If `main` is too moving-target for your project, try a known older stable tag instead.

Example pattern:

```bash
pip uninstall -y lerobot
pip install "lerobot[smolvla,libero]==<stable-version>"
python -m pip install num2words
```

Before choosing a pinned version, check which version still supports the SmolVLA and LIBERO workflow you want.

### Option 3: Patch the broken config locally

If you must stay on the installed package, inspect:

```text
.../site-packages/lerobot/policies/groot/groot_n1.py
```

The failure is consistent with a dataclass field-ordering problem in `GR00TN15Config`, where non-default `init=False` fields appear before a default-valued field. A local patch or upstream fix to that config can unblock imports.

For this repo, there is also a helper patch script:

```bash
python scripts/patch_lerobot_groot_import.py /home/kevin/miniforge3/envs/lerobot/lib/python3.12/site-packages
```

That patch makes LeRobot tolerate the GROOT import failure so `lerobot-eval` can continue loading other policies such as SmolVLA.

### Option 4: Use the LeRobot CLI instead of direct import

If your goal is evaluation or training rather than a custom Python script, try the CLI path first:

```bash
lerobot-eval --help
lerobot-train --help
```

For some environments, the CLI route can be easier to keep aligned with the exact LeRobot version and policy config flow than a custom direct-import script.

## Additional dependency note

Even after the GROOT import workaround, SmolVLA loading may still fail if `num2words` is missing. The underlying SmolVLM processor requires it.

Install it with:

```bash
python -m pip install num2words
```

## LIBERO evaluation placeholder

There is also a helper script:

```bash
bash scripts/run_libero_eval.sh
```

It contains a placeholder `lerobot-eval` command for a LIBERO benchmark run. The important caveat is that `smolvla_base` is a base pretrained model, so a LIBERO-finetuned checkpoint may be needed for meaningful benchmark performance.

## Next milestone

The next milestone is to run a simple LIBERO pick/place simulation and then replace the placeholder checkpoint with a task-adapted policy checkpoint that responds to a language instruction such as "pick up the object and place it in the target area."

## Reference notes

This repo is aligned with the current Hugging Face LeRobot documentation for:

- SmolVLA setup
- LIBERO support on Linux
- model ID `lerobot/smolvla_base`
