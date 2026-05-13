from __future__ import annotations

from pathlib import Path
import re
import textwrap

CONFIG_PATH = Path("/home/kevin/.libero/config.yaml")
CUSTOM_BDDL = Path("custom_libero_tasks/Kevins_custom_suite/yellow_mug_to_basket.bddl")
CACHE_ASSETS = Path("/home/kevin/.cache/libero/assets")


def parse_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line or line.startswith("-"):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def extract_objects(bddl_text: str) -> list[tuple[str, str]]:
    object_pairs: list[tuple[str, str]] = []
    in_objects = False
    for raw_line in bddl_text.splitlines():
        line = raw_line.strip()
        if line.startswith("(:objects"):
            in_objects = True
            continue
        if in_objects and line == ")":
            break
        if in_objects and " - " in line:
            names_part, type_part = line.split(" - ", 1)
            object_type = type_part.strip()
            for object_name in names_part.split():
                object_pairs.append((object_name.strip(), object_type))
    return object_pairs


def print_summary(bddl_text: str) -> None:
    language_match = re.search(r"\(:language\s+(.+?)\)", bddl_text, flags=re.DOTALL)
    goal_match = re.search(r"\(:goal\s+(.+?)\)\s*\)\s*$", bddl_text, flags=re.DOTALL)
    print("Custom BDDL summary:")
    if language_match:
        print(f"  language: {language_match.group(1).strip()}")
    else:
        print("  language: <not found>")

    object_pairs = extract_objects(bddl_text)
    print("  objects:")
    for object_name, object_type in object_pairs:
        print(f"    - {object_name}: {object_type}")

    if goal_match:
        compact_goal = " ".join(goal_match.group(1).split())
        print(f"  goal: {compact_goal}")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    bddl_path = repo_root / CUSTOM_BDDL

    print(f"Checking custom BDDL file: {bddl_path}")
    if not bddl_path.exists():
        print("ERROR: custom BDDL file does not exist.")
        return 1

    bddl_text = bddl_path.read_text()
    print()
    print_summary(bddl_text)
    print()

    print("Full BDDL contents:")
    print(textwrap.indent(bddl_text, "  "))
    print()

    from libero.libero.envs.objects import OBJECTS_DICT
    from libero.libero.envs.env_wrapper import ControlEnv

    cfg = parse_simple_yaml(CONFIG_PATH)
    assets_root = Path(cfg.get("assets", ""))

    object_pairs = extract_objects(bddl_text)
    object_types = sorted({object_type for _, object_type in object_pairs})

    print("Object registry checks:")
    for object_type in object_types:
        exists = object_type in OBJECTS_DICT
        print(f"  {object_type}: {'OK' if exists else 'MISSING'}")
    print()

    print("Asset path hints:")
    for object_type in object_types:
        asset_hits: list[Path] = []
        for root in [assets_root, CACHE_ASSETS]:
            if root.exists():
                asset_hits.extend(sorted(root.rglob(f"*{object_type}*")))
        deduped_hits = []
        seen = set()
        for path in asset_hits:
            if path not in seen:
                deduped_hits.append(path)
                seen.add(path)
        if deduped_hits:
            print(f"  {object_type}:")
            for asset_path in deduped_hits[:8]:
                print(f"    - {asset_path}")
        else:
            print(f"  {object_type}: no direct asset filename match under {assets_root} or {CACHE_ASSETS}")
    print()

    print("Attempting direct environment load from the custom BDDL file...")
    try:
        env = ControlEnv(
            bddl_file_name=str(bddl_path),
            has_renderer=False,
            has_offscreen_renderer=True,
            camera_heights=128,
            camera_widths=128,
            camera_names=["agentview", "robot0_eye_in_hand"],
        )
        obs = env.reset()
        print("SUCCESS: ControlEnv loaded the custom BDDL file.")
        print(f"Observation keys: {sorted(obs.keys())[:12]}")
        env.close()
    except Exception as exc:
        print(f"Direct ControlEnv load failed: {exc}")
        print("Next steps:")
        print("  - Inspect the object names and scene/problem name in the custom BDDL.")
        print("  - Compare this BDDL against the built-in basket and mug templates.")
        print("  - If needed, adjust regions or object types to match LIBERO's supported scenes.")
        return 1

    print()
    print("Benchmark registration note:")
    print("  This repo-local BDDL can be loaded directly, but the suite name 'Kevins_custom_suite'")
    print("  is not automatically registered in the installed LIBERO benchmark registry.")
    print("  Built-in LIBERO benchmark registration is defined in:")
    print("    - libero/libero/benchmark/libero_suite_task_map.py")
    print("    - libero/libero/benchmark/__init__.py")
    print("  A full benchmark-style suite would also need matching init-state handling.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
