from __future__ import annotations

from pathlib import Path


KEYWORDS = ["mug", "yellow", "white", "basket", "container", "bowl", "tray"]
CONFIG_PATH = Path("/home/kevin/.libero/config.yaml")
CACHE_ASSETS = Path("/home/kevin/.cache/libero/assets")


def parse_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def find_bddl_matches(bddl_root: Path) -> list[tuple[Path, str]]:
    matches: list[tuple[Path, str]] = []
    if not bddl_root.exists():
        return matches

    for path in sorted(bddl_root.rglob("*.bddl")):
        text = path.read_text(errors="ignore").lower()
        hit_words = [word for word in KEYWORDS if word in text or word in path.name.lower()]
        if hit_words:
            matches.append((path, ", ".join(hit_words)))
    return matches


def find_asset_matches(asset_roots: list[Path]) -> list[tuple[Path, str]]:
    matches: list[tuple[Path, str]] = []
    seen: set[Path] = set()
    for root in asset_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            lowered = str(path).lower()
            hit_words = [word for word in KEYWORDS if word in lowered]
            if hit_words and path not in seen:
                matches.append((path, ", ".join(hit_words)))
                seen.add(path)
    return matches


def main() -> int:
    cfg = parse_simple_yaml(CONFIG_PATH)
    bddl_root = Path(cfg.get("bddl_files", ""))
    assets_root = Path(cfg.get("assets", ""))

    print("LIBERO config file:")
    print(f"  {CONFIG_PATH}")
    print()
    print("Configured paths:")
    print(f"  bddl_files: {bddl_root}")
    print(f"  assets: {assets_root}")
    print(f"  cache assets: {CACHE_ASSETS}")
    print()

    print("Matching BDDL files:")
    for path, words in find_bddl_matches(bddl_root):
        print(f"  [{words}] {path}")
    print()

    print("Matching asset paths:")
    for path, words in find_asset_matches([assets_root, CACHE_ASSETS]):
        print(f"  [{words}] {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
