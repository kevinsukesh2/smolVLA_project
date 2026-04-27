from __future__ import annotations

import sys


def check_python() -> bool:
    version = sys.version_info
    print(f"[INFO] Python version: {version.major}.{version.minor}.{version.micro}")
    if version < (3, 10):
        print("[FAIL] Python 3.10+ is recommended for modern LeRobot setups.")
        return False
    print("[ OK ] Python version looks compatible.")
    return True


def check_torch() -> bool:
    try:
        import torch
    except Exception as exc:
        print(f"[FAIL] Could not import torch: {exc}")
        return False

    print(f"[INFO] torch version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"[INFO] CUDA available: {cuda_available}")
    if cuda_available:
        print(f"[INFO] CUDA device count: {torch.cuda.device_count()}")
    print("[ OK ] torch import succeeded.")
    return True


def check_lerobot() -> bool:
    try:
        import lerobot  # noqa: F401
    except Exception as exc:
        print(f"[FAIL] Could not import lerobot: {exc}")
        return False

    print("[ OK ] lerobot import succeeded.")
    return True


def main() -> int:
    print("Running installation checks for LeRobot + SmolVLA...")
    print("-" * 60)

    checks = [
        check_python(),
        check_torch(),
        check_lerobot(),
    ]

    print("-" * 60)
    if all(checks):
        print("[SUCCESS] Environment checks passed.")
        return 0

    print("[FAILURE] One or more checks failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
