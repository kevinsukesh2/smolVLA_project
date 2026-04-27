#!/usr/bin/env bash

set -euo pipefail

# This script is intended for WSL2 Ubuntu.
# It installs basic system dependencies, creates or reuses a Conda
# environment named "lerobot", and installs LeRobot with SmolVLA
# and LIBERO simulation support.

ENV_NAME="lerobot"
PYTHON_VERSION="3.12"
LEROBOT_SRC_DIR="${HOME}/.cache/lerobot-src"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Starting LeRobot + SmolVLA setup for WSL2 Ubuntu"

# Check that we are on Linux, because LIBERO support in LeRobot is Linux-only.
if [[ "$(uname -s)" != "Linux" ]]; then
    echo "This setup script expects Linux. WSL2 Ubuntu is recommended."
    exit 1
fi

# Check that conda is available.
if ! command -v conda >/dev/null 2>&1; then
    echo "Conda was not found in PATH."
    echo "Please install Miniforge or Conda first, then re-run this script."
    exit 1
fi

# Install basic Ubuntu packages used by common Python/native builds and video tooling.
# We keep this list modest and avoid ROS/Gazebo entirely.
if command -v apt-get >/dev/null 2>&1; then
    echo "==> Installing/checking Ubuntu packages"
    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        cmake \
        git \
        ffmpeg \
        pkg-config \
        python3-dev \
        libavformat-dev \
        libavcodec-dev \
        libavdevice-dev \
        libavutil-dev \
        libswscale-dev \
        libswresample-dev \
        libavfilter-dev
fi

# Make sure the conda shell function is available in this script.
eval "$(conda shell.bash hook)"

# Create the environment if it does not already exist.
if conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
    echo "==> Reusing existing conda environment: ${ENV_NAME}"
else
    echo "==> Creating conda environment: ${ENV_NAME} (python=${PYTHON_VERSION})"
    conda create -y -n "${ENV_NAME}" "python=${PYTHON_VERSION}"
fi

echo "==> Activating conda environment: ${ENV_NAME}"
conda activate "${ENV_NAME}"

# The LeRobot installation docs call out evdev specifically for WSL.
echo "==> Installing Conda packages needed for WSL/video support"
conda install -y -c conda-forge evdev ffmpeg

# Upgrade core packaging tools before installing LeRobot.
echo "==> Upgrading pip tooling"
python -m pip install --upgrade pip setuptools wheel

# Install the small validation dependencies listed in requirements.txt.
# This also includes num2words, which is needed by the SmolVLM processor
# used under the hood by SmolVLA model loading.
echo "==> Installing minimal Python requirements"
python -m pip install -r "${SCRIPT_DIR}/requirements.txt"

# Install LeRobot from source so we can add the SmolVLA and LIBERO extras
# exactly as described in the Hugging Face docs.
if [[ ! -d "${LEROBOT_SRC_DIR}/.git" ]]; then
    echo "==> Cloning LeRobot source into ${LEROBOT_SRC_DIR}"
    git clone https://github.com/huggingface/lerobot.git "${LEROBOT_SRC_DIR}"
else
    echo "==> Updating existing LeRobot source checkout in ${LEROBOT_SRC_DIR}"
    git -C "${LEROBOT_SRC_DIR}" pull --ff-only
fi

echo "==> Installing LeRobot with SmolVLA and LIBERO extras"
python -m pip install -e "${LEROBOT_SRC_DIR}[smolvla,libero]"

# Headless rendering is often the safest default for WSL/cloud-style setups.
export MUJOCO_GL=egl

echo
echo "Setup complete."
echo "Next steps:"
echo "  conda activate ${ENV_NAME}"
echo "  python scripts/test_install.py"
echo "  python scripts/load_smolvla.py"
echo
echo "Suggested environment variable for headless simulation:"
echo "  export MUJOCO_GL=egl"
