# Kevins_custom_suite Research Notes

## Goal

Create a repo-local custom LIBERO task suite attempt named `Kevins_custom_suite` with a task that means:

- pick up the yellow mug
- place it in the basket

Language instruction:

- `Pick up the yellow mug and place it in the basket.`

## Installed LIBERO Configuration

Config file:

- `/home/kevin/.libero/config.yaml`

Configured paths:

- `bddl_files`: `/home/kevin/miniforge3/envs/lerobot/lib/python3.12/site-packages/libero/libero/bddl_files`
- `init_states`: `/home/kevin/miniforge3/envs/lerobot/lib/python3.12/site-packages/libero/libero/init_files`
- `assets`: `/home/kevin/miniforge3/envs/lerobot/lib/python3.12/site-packages/libero/libero/assets`

Observed asset cache:

- `/home/kevin/.cache/libero/assets`

## Similar Existing Tasks Found

Closest basket-placement template:

- `libero_object/pick_up_the_alphabet_soup_and_place_it_in_the_basket.bddl`

Closest mug tasks:

- `libero_90/LIVING_ROOM_SCENE5_put_the_yellow_and_white_mug_on_the_right_plate.bddl`
- `libero_90/LIVING_ROOM_SCENE5_put_the_white_mug_on_the_left_plate.bddl`
- `libero_10/KITCHEN_SCENE6_put_the_yellow_and_white_mug_in_the_microwave_and_close_it.bddl`

These showed that LIBERO already uses:

- `white_yellow_mug`
- `porcelain_mug`
- `basket`

## Template Choice

Primary BDDL syntax/template source:

- `libero_object/pick_up_the_alphabet_soup_and_place_it_in_the_basket.bddl`

Reason:

- it already defines a floor manipulation scene with a basket containment goal
- it is the closest match to the requested task structure

Object naming references taken from:

- `LIVING_ROOM_SCENE5_put_the_yellow_and_white_mug_on_the_right_plate.bddl`
- `LIVING_ROOM_SCENE5_put_the_white_mug_on_the_left_plate.bddl`
- LIBERO object registry in `libero/libero/envs/objects`

## Reused Object Names / Asset Notes

Verified installed object names:

- `white_yellow_mug`
- `porcelain_mug`
- `basket`

Verified asset cache matches:

- `turbosquid_objects/white_yellow_mug`
- `turbosquid_objects/porcelain_mug`
- `stable_scanned_objects/basket`

## Substitutions Used

Exact requested objects were not both available as separate object types.

Used substitutions:

- requested `yellow mug` -> reused `white_yellow_mug`
- requested `white mug` -> reused `porcelain_mug`

This was done intentionally and explicitly, not silently.

## Custom BDDL Location

- `custom_libero_tasks/Kevins_custom_suite/yellow_mug_to_basket.bddl`

## What Still Needs To Be Done

To make `Kevins_custom_suite` work as a true LIBERO benchmark suite name, more registration work is needed.

Likely installed-package files involved:

- `libero/libero/benchmark/libero_suite_task_map.py`
- `libero/libero/benchmark/__init__.py`

Why:

- built-in benchmark suites are hardcoded there
- task names are mapped to BDDL filenames and init-state filenames there

Additional likely requirement:

- create or generate a matching init-state file if using the full benchmark API

Repo-local progress already possible:

- inspect the custom BDDL
- verify object names/assets
- attempt direct environment loading from the BDDL file using `ControlEnv`

## Recommended Next Step

First confirm that the repo-local BDDL can be loaded directly.

Use:

- `python scripts/test_kevins_custom_suite.py`

Only after that should benchmark registration or LeRobot integration changes be considered.
