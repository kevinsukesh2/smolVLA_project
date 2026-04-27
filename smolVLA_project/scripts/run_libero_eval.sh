#!/usr/bin/env bash

set -euo pipefail

# This is a placeholder helper for running a LIBERO evaluation with LeRobot.
# It does not launch training. It shows the expected command shape for eval.
#
# Important:
# - LIBERO support is Linux-only in the current LeRobot docs.
# - Headless simulation commonly uses MUJOCO_GL=egl.
# - A LIBERO-finetuned checkpoint may be needed for meaningful results.
#   The base checkpoint "lerobot/smolvla_base" is a foundation model, not a
#   benchmark-specialized policy.

export MUJOCO_GL="${MUJOCO_GL:-egl}"

POLICY_PATH="${1:-your-libero-finetuned-checkpoint}"
TASK_SUITE="${2:-libero_object}"
EPISODES="${3:-2}"

echo "MUJOCO_GL=${MUJOCO_GL}"
echo "Policy checkpoint: ${POLICY_PATH}"
echo "LIBERO task suite: ${TASK_SUITE}"
echo "Episodes: ${EPISODES}"
echo
echo "Example command:"

cat <<EOF
lerobot-eval \
  --policy.path="${POLICY_PATH}" \
  --env.type=libero \
  --env.task="${TASK_SUITE}" \
  --eval.batch_size=1 \
  --eval.n_episodes="${EPISODES}" \
  --env.max_parallel_tasks=1
EOF

echo
echo "Replace '${POLICY_PATH}' with a checkpoint that is compatible with LIBERO."
