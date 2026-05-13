from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from live_libero_viewer import DEFAULT_POLICY_PATH, DEFAULT_TASK_SUITE, get_task_metadata

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ImportError as exc:
    raise SystemExit(
        "tkinter is not available in this Python environment.\n"
        "On WSL Ubuntu, install it with:\n"
        "  sudo apt install python3-tk\n"
    ) from exc


SCRIPT_PATH = Path(__file__).resolve().parent / "live_libero_viewer.py"
KNOWN_SUITES = [
    "libero_object",
    "Kevins_custom_suite",
    "libero_spatial",
    "libero_goal",
    "libero_10",
    "libero_90",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LIBERO task selector GUI for the SmolVLA live demo.")
    parser.add_argument(
        "--task-suite",
        default=DEFAULT_TASK_SUITE,
        help="LIBERO task suite to list first, for example libero_object.",
    )
    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="Print task metadata to the terminal and exit without launching the GUI.",
    )
    return parser.parse_args()


def print_task_list(task_suite: str) -> None:
    # A LIBERO task suite is a benchmark group such as libero_object.
    # Each task in the suite has a stable integer task_id and a language instruction.
    for task in get_task_metadata(task_suite):
        bddl_text = task.bddl_filename or "<unknown>"
        print(f"{task.task_id}\t{bddl_text}\t{task.language_instruction}")


class LiberoTaskGui:
    def __init__(self, root: tk.Tk, initial_suite: str):
        self.root = root
        self.root.title("SmolVLA LIBERO Task Selector")
        self.root.geometry("900x520")

        self.policy_path_var = tk.StringVar(value=DEFAULT_POLICY_PATH)
        self.max_steps_var = tk.StringVar(value="")
        self.sleep_var = tk.StringVar(value="0.0")
        self.task_suite_var = tk.StringVar(value=initial_suite)
        self.selected_instruction_var = tk.StringVar(value="Select a task to view its instruction.")
        self.selected_bddl_var = tk.StringVar(value="BDDL: ")
        self.status_var = tk.StringVar(
            value="Task metadata only is loaded here. The live environment is created only when you click Run."
        )
        self.tasks = []

        self._build_layout()
        self.reload_tasks()

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(3, weight=1)

        ttk.Label(main, text="LIBERO Task Suite").grid(row=0, column=0, sticky="w")
        suite_combo = ttk.Combobox(
            main,
            textvariable=self.task_suite_var,
            values=KNOWN_SUITES,
            state="readonly",
        )
        suite_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        suite_combo.bind("<<ComboboxSelected>>", lambda _event: self.reload_tasks())

        ttk.Button(main, text="Reload Tasks", command=self.reload_tasks).grid(row=1, column=1, sticky="ew")

        # We show one task at a time in the viewer because creating all LIBERO environments
        # at once uses much more RAM. The GUI only lists metadata first.
        self.task_list = tk.Listbox(main, exportselection=False, height=16)
        self.task_list.grid(row=3, column=0, sticky="nsew", padx=(0, 8), pady=(12, 0))
        self.task_list.bind("<<ListboxSelect>>", lambda _event: self.on_task_selected())

        right = ttk.Frame(main)
        right.grid(row=3, column=1, sticky="nsew", pady=(12, 0))
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Selected Instruction").grid(row=0, column=0, sticky="w")
        ttk.Label(
            right,
            textvariable=self.selected_instruction_var,
            wraplength=360,
            justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(4, 8))
        ttk.Label(right, textvariable=self.selected_bddl_var, wraplength=360, justify="left").grid(
            row=2, column=0, sticky="ew", pady=(0, 12)
        )

        ttk.Label(right, text="Policy Path").grid(row=3, column=0, sticky="w")
        ttk.Entry(right, textvariable=self.policy_path_var).grid(row=4, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(right, text="Max Steps (optional)").grid(row=5, column=0, sticky="w")
        ttk.Entry(right, textvariable=self.max_steps_var).grid(row=6, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(right, text="Sleep Delay (seconds)").grid(row=7, column=0, sticky="w")
        ttk.Entry(right, textvariable=self.sleep_var).grid(row=8, column=0, sticky="ew", pady=(0, 12))

        ttk.Button(right, text="Run Selected Task", command=self.run_selected_task).grid(
            row=9, column=0, sticky="ew"
        )

        ttk.Label(main, textvariable=self.status_var, wraplength=860, justify="left").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )

    def reload_tasks(self) -> None:
        suite_name = self.task_suite_var.get().strip()
        self.tasks = get_task_metadata(suite_name)
        self.task_list.delete(0, tk.END)

        for task in self.tasks:
            bddl_text = task.bddl_filename or "<unknown>"
            self.task_list.insert(
                tk.END,
                f"{task.task_id}: {task.language_instruction} [{bddl_text}]",
            )

        if self.tasks:
            self.task_list.selection_set(0)
            self.on_task_selected()
            self.status_var.set(f"Loaded {len(self.tasks)} tasks from suite '{suite_name}'.")
        else:
            self.selected_instruction_var.set("No tasks found.")
            self.selected_bddl_var.set("BDDL: ")
            self.status_var.set(f"No tasks found for suite '{suite_name}'.")

    def get_selected_task(self):
        selection = self.task_list.curselection()
        if not selection:
            return None
        return self.tasks[selection[0]]

    def on_task_selected(self) -> None:
        task = self.get_selected_task()
        if task is None:
            self.selected_instruction_var.set("Select a task to view its instruction.")
            self.selected_bddl_var.set("BDDL: ")
            return

        self.selected_instruction_var.set(task.language_instruction)
        self.selected_bddl_var.set(f"BDDL: {task.bddl_filename or '<unknown>'}")

    def run_selected_task(self) -> None:
        task = self.get_selected_task()
        if task is None:
            messagebox.showwarning("No task selected", "Please select a LIBERO task first.")
            return

        command = [
            sys.executable,
            str(SCRIPT_PATH),
            "--task-suite",
            self.task_suite_var.get().strip(),
            "--task-id",
            str(task.task_id),
            "--policy-path",
            self.policy_path_var.get().strip() or DEFAULT_POLICY_PATH,
        ]

        max_steps = self.max_steps_var.get().strip()
        if max_steps:
            command.extend(["--max-steps", max_steps])

        sleep_delay = self.sleep_var.get().strip()
        if sleep_delay:
            command.extend(["--sleep", sleep_delay])

        try:
            subprocess.Popen(command)
        except Exception as exc:
            messagebox.showerror("Launch failed", f"Could not launch the live viewer:\n{exc}")
            return

        self.status_var.set(
            f"Launched task_id={task.task_id} from suite '{self.task_suite_var.get().strip()}'."
        )


def main() -> int:
    args = parse_args()
    if args.list_tasks:
        print_task_list(args.task_suite)
        return 0

    root = tk.Tk()
    LiberoTaskGui(root, args.task_suite)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
