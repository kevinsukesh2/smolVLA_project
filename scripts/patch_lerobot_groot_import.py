from __future__ import annotations

import sys
from pathlib import Path


POLICIES_INIT = """# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings

from .act.configuration_act import ACTConfig as ACTConfig
from .diffusion.configuration_diffusion import DiffusionConfig as DiffusionConfig
from .multi_task_dit.configuration_multi_task_dit import MultiTaskDiTConfig as MultiTaskDiTConfig
from .pi0.configuration_pi0 import PI0Config as PI0Config
from .pi0_fast.configuration_pi0_fast import PI0FastConfig as PI0FastConfig
from .pi05.configuration_pi05 import PI05Config as PI05Config
from .smolvla.configuration_smolvla import SmolVLAConfig as SmolVLAConfig
from .smolvla.processor_smolvla import SmolVLANewLineProcessor
from .tdmpc.configuration_tdmpc import TDMPCConfig as TDMPCConfig
from .vqbet.configuration_vqbet import VQBeTConfig as VQBeTConfig
from .wall_x.configuration_wall_x import WallXConfig as WallXConfig
from .xvla.configuration_xvla import XVLAConfig as XVLAConfig

try:
    from .groot.configuration_groot import GrootConfig as GrootConfig
except TypeError as exc:
    if "backbone_cfg" not in str(exc):
        raise
    warnings.warn(
        "Skipping GROOT policy imports because LeRobot's installed GROOT package "
        "hits a Python 3.12 dataclass bug: "
        f"{exc}. SmolVLA and other policies remain available.",
        RuntimeWarning,
    )
    GrootConfig = None

__all__ = [
    "ACTConfig",
    "DiffusionConfig",
    "MultiTaskDiTConfig",
    "PI0Config",
    "PI05Config",
    "PI0FastConfig",
    "SmolVLAConfig",
    "SARMConfig",
    "TDMPCConfig",
    "VQBeTConfig",
    "GrootConfig",
    "XVLAConfig",
    "WallXConfig",
]
"""


GROOT_INIT = """#!/usr/bin/env python

# Copyright 2025 Nvidia and The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings

from .configuration_groot import GrootConfig

try:
    from .modeling_groot import GrootPolicy
except TypeError as exc:
    if "backbone_cfg" not in str(exc):
        raise
    warnings.warn(
        "Skipping GrootPolicy import because the installed GROOT model code hits "
        f"a Python 3.12 dataclass bug: {exc}",
        RuntimeWarning,
    )
    GrootPolicy = None

from .processor_groot import make_groot_pre_post_processors

__all__ = ["GrootConfig", "GrootPolicy", "make_groot_pre_post_processors"]
"""


def write_file(path: Path, content: str) -> None:
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(content, encoding="utf-8")
    print(f"Patched {path}")
    print(f"Backup  {backup}")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/patch_lerobot_groot_import.py /path/to/site-packages")
        return 1

    site_packages = Path(sys.argv[1]).expanduser().resolve()
    policies_init = site_packages / "lerobot" / "policies" / "__init__.py"
    groot_init = site_packages / "lerobot" / "policies" / "groot" / "__init__.py"

    for path in [policies_init, groot_init]:
        if not path.exists():
            print(f"Missing expected file: {path}")
            return 1

    write_file(policies_init, POLICIES_INIT)
    write_file(groot_init, GROOT_INIT)
    print("LeRobot GROOT import patch applied successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
