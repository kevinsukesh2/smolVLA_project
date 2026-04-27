from __future__ import annotations

import argparse
import importlib
import pkgutil
import subprocess
import sys
import traceback
import types
from pathlib import Path

import torch


def run_command(args: list[str]) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=False)
    except Exception as exc:
        return f"[command failed to start] {exc}"

    output = result.stdout.strip()
    error = result.stderr.strip()

    if output and error:
        return f"{output}\n{error}"
    if output:
        return output
    if error:
        return error
    return f"[no output, exit code={result.returncode}]"


def print_diagnostics() -> None:
    print()
    print("=== Diagnostic mode ===")

    try:
        import lerobot
    except Exception as exc:
        print(f"lerobot import failed during diagnostics: {exc}")
        return

    print(f"lerobot.__file__: {lerobot.__file__}")
    print()
    print("pip show lerobot:")
    print(run_command([sys.executable, "-m", "pip", "show", "lerobot"]))
    print()

    print("Available top-level modules under lerobot:")
    try:
        for module in sorted(m.name for m in pkgutil.iter_modules(lerobot.__path__)):
            print(f"  - {module}")
    except Exception as exc:
        print(f"  [failed to enumerate modules] {exc}")
    print()

    print("Files matching *smolvla*:")
    try:
        root = Path(lerobot.__file__).resolve().parent
        matches = sorted(root.rglob("*smolvla*"))
        if matches:
            for path in matches:
                print(f"  - {path}")
        else:
            print("  [no smolvla files found]")
    except Exception as exc:
        print(f"  [failed to search for smolvla files] {exc}")
    print()


def make_policies_stub() -> None:
    import lerobot

    root = Path(lerobot.__file__).resolve().parent
    policies_dir = root / "policies"

    stub = types.ModuleType("lerobot.policies")
    stub.__path__ = [str(policies_dir)]
    stub.__file__ = str(policies_dir / "__init__.py")
    stub.__package__ = "lerobot.policies"
    sys.modules["lerobot.policies"] = stub


def import_policy_class():
    try:
        from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy

        print("Imported SmolVLAPolicy through the standard LeRobot package path.")
        return SmolVLAPolicy
    except Exception as exc:
        print(f"Standard SmolVLA import failed: {exc}")

        # LeRobot 0.5.1 can fail here because importing lerobot.policies triggers
        # eager imports of unrelated policies, including GROOT, whose config can
        # raise a dataclass field-ordering error on Python 3.12.
        if "backbone_cfg" not in str(exc):
            raise

        print("Trying SmolVLA-only import workaround for the GROOT dataclass bug...")
        make_policies_stub()
        module = importlib.import_module("lerobot.policies.smolvla.modeling_smolvla")
        print("Imported SmolVLAPolicy through the SmolVLA-only fallback path.")
        return module.SmolVLAPolicy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load the LeRobot SmolVLA base model.")
    parser.add_argument(
        "--model-id",
        default="lerobot/smolvla_base",
        help="Hugging Face model ID to load.",
    )
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Print LeRobot package diagnostics before attempting model load.",
    )
    parser.add_argument(
        "--diagnose-only",
        action="store_true",
        help="Only print diagnostics and exit without loading the model.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_id = args.model_id
    print(f"Loading SmolVLA model: {model_id}")

    if args.diagnose or args.diagnose_only:
        print_diagnostics()

    if args.diagnose_only:
        return 0

    try:
        SmolVLAPolicy = import_policy_class()
    except Exception as exc:
        print(f"Failed to import SmolVLAPolicy: {exc}")
        traceback.print_exc()
        print_diagnostics()
        return 1

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    try:
        policy = SmolVLAPolicy.from_pretrained(model_id)
        policy = policy.to(device).eval()
    except ImportError as exc:
        print(f"Failed to load model '{model_id}': {exc}")
        if "num2words" in str(exc):
            print("Hint: SmolVLM's processor requires the 'num2words' package.")
            print("Install it in your active environment with:")
            print("  python -m pip install num2words")
        print_diagnostics()
        return 1
    except Exception as exc:
        print(f"Failed to load model '{model_id}': {exc}")
        traceback.print_exc()
        print_diagnostics()
        return 1

    print(f"Model loaded successfully: {model_id}")
    print(f"Policy class: {policy.__class__.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
