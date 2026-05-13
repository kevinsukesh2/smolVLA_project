# Kevins_custom_suite

This folder contains a repo-local custom LIBERO task attempt for the SmolVLA project.

## Goal

Target task:

- pick up the yellow mug
- place it in the basket

Requested language instruction:

- `Pick up the yellow mug and place it in the basket.`

## Important Asset Reuse Notes

This custom task reuses object names that already exist in the installed LIBERO package.

Reused object names:

- `white_yellow_mug`
  Used as the closest available substitute for a yellow mug.
- `porcelain_mug`
  Used as the closest available substitute for a white mug.
- `basket`
  Reused directly.

Why substitutions were needed:

- An exact standalone `yellow_mug` object name was not found in the installed LIBERO object registry.
- An exact standalone `white_mug` object name was not found as an object type in the registry.
- The installed registry does include `white_yellow_mug`, `porcelain_mug`, and `basket`.

## Files

- `yellow_mug_to_basket.bddl`
  Repo-local BDDL task definition based on the built-in LIBERO basket task style.

## Current Limitation

This folder does not automatically register a new benchmark suite into the installed LIBERO package.

That means:

- the BDDL file can be inspected and potentially loaded directly
- but `--task-suite Kevins_custom_suite` will not work with built-in LIBERO benchmark lookup until a registration step is added

See:

- `notes/kevins_custom_suite_research.md`
- `scripts/test_kevins_custom_suite.py`
