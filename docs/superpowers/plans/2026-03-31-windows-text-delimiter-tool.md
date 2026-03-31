# Windows Text Delimiter Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Windows desktop utility that converts pasted multi-line text into delimiter-formatted output with presets and customizable prefix, suffix, and delimiter controls.

**Architecture:** Use Python with Tkinter for a single-window desktop UI. Keep text transformation logic in a separate pure-Python module so it can be tested independently from the GUI. Wire Tkinter input and controls to recompute output on every relevant change.

**Tech Stack:** Python 3, Tkinter, unittest

---

## File Structure

- Create: `src/text_delimiter_tool/__init__.py`
- Create: `src/text_delimiter_tool/formatter.py`
- Create: `src/text_delimiter_tool/app.py`
- Create: `tests/test_formatter.py`
- Create: `run_app.py`
- Create: `README.md`

Responsibilities:

- `src/text_delimiter_tool/formatter.py`: pure formatting logic and settings model
- `src/text_delimiter_tool/app.py`: Tkinter window, layout, event bindings, and button handlers
- `tests/test_formatter.py`: automated coverage for formatting rules
- `run_app.py`: local application entry point
- `README.md`: local run instructions and feature summary

### Task 1: Create package skeleton

**Files:**
- Create: `src/text_delimiter_tool/__init__.py`
- Create: `run_app.py`

- [ ] **Step 1: Create the package marker file**

```python
"""Text delimiter tool package."""
```

- [ ] **Step 2: Create the application entry point stub**

```python
from text_delimiter_tool.app import main


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the entry point to verify the import fails before implementation exists**

Run: `python run_app.py`
Expected: FAIL with `ModuleNotFoundError` for `text_delimiter_tool.app`

- [ ] **Step 4: Commit**

```bash
git add src/text_delimiter_tool/__init__.py run_app.py
git commit -m "chore: add app package skeleton"
```

### Task 2: Build the formatter with the first failing test

**Files:**
- Create: `src/text_delimiter_tool/formatter.py`
- Create: `tests/test_formatter.py`
- Modify: `src/text_delimiter_tool/__init__.py`

- [ ] **Step 1: Write the failing test for basic comma formatting**

```python
import unittest

from text_delimiter_tool.formatter import FormatOptions, format_lines


class FormatterTests(unittest.TestCase):
    def test_formats_multiple_lines_with_commas_between_items(self) -> None:
        result = format_lines(
            "1\n2\n3",
            FormatOptions(prefix="", suffix="", delimiter=",", trailing_delimiter=False),
        )

        self.assertEqual(result, "1,\n2,\n3")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails for the expected reason**

Run: `set PYTHONPATH=src && python -m unittest tests.test_formatter -v`
Expected: FAIL with `ModuleNotFoundError` for `text_delimiter_tool.formatter`

- [ ] **Step 3: Write the minimal formatter implementation**

```python
from dataclasses import dataclass


@dataclass(slots=True)
class FormatOptions:
    prefix: str
    suffix: str
    delimiter: str
    trailing_delimiter: bool


def format_lines(raw_text: str, options: FormatOptions) -> str:
    values = [line.strip() for line in raw_text.splitlines() if line.strip()]
    formatted = []

    for index, value in enumerate(values):
        is_last = index == len(values) - 1
        append_delimiter = options.trailing_delimiter or not is_last
        tail = options.delimiter if append_delimiter else ""
        formatted.append(f"{options.prefix}{value}{options.suffix}{tail}")

    return "\n".join(formatted)
```

- [ ] **Step 4: Export the formatter types from the package marker**

```python
from text_delimiter_tool.formatter import FormatOptions, format_lines

__all__ = ["FormatOptions", "format_lines"]
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `set PYTHONPATH=src && python -m unittest tests.test_formatter -v`
Expected: PASS for `test_formats_multiple_lines_with_commas_between_items`

- [ ] **Step 6: Commit**

```bash
git add src/text_delimiter_tool/__init__.py src/text_delimiter_tool/formatter.py tests/test_formatter.py
git commit -m "feat: add core line formatter"
```

### Task 3: Add formatter edge-case coverage

**Files:**
- Modify: `tests/test_formatter.py`
- Modify: `src/text_delimiter_tool/formatter.py`

- [ ] **Step 1: Add failing tests for whitespace trimming, empty-line removal, empty input, and trailing delimiter mode**

```python
    def test_trims_whitespace_and_skips_blank_lines(self) -> None:
        result = format_lines(
            "  1  \n\n   2\n  \n3  ",
            FormatOptions(prefix="'", suffix="'", delimiter=",", trailing_delimiter=False),
        )

        self.assertEqual(result, "'1',\n'2',\n'3'")

    def test_adds_delimiter_to_every_line_when_enabled(self) -> None:
        result = format_lines(
            "1\n2\n3",
            FormatOptions(prefix="'", suffix="'", delimiter=",", trailing_delimiter=True),
        )

        self.assertEqual(result, "'1',\n'2',\n'3',")

    def test_returns_empty_string_for_empty_input(self) -> None:
        result = format_lines(
            "\n  \n",
            FormatOptions(prefix="", suffix="", delimiter=",", trailing_delimiter=False),
        )

        self.assertEqual(result, "")

    def test_allows_empty_prefix_suffix_and_delimiter(self) -> None:
        result = format_lines(
            "a\nb",
            FormatOptions(prefix="", suffix="", delimiter="", trailing_delimiter=False),
        )

        self.assertEqual(result, "a\nb")
```

- [ ] **Step 2: Run the tests to verify the new case for trailing delimiter fails first**

Run: `set PYTHONPATH=src && python -m unittest tests.test_formatter -v`
Expected: FAIL on `test_adds_delimiter_to_every_line_when_enabled` if implementation is incomplete, or PASS only after confirming the test was added correctly and any failure came from the expected behavior gap

- [ ] **Step 3: Adjust the formatter only if needed to satisfy the new tests**

```python
def format_lines(raw_text: str, options: FormatOptions) -> str:
    values = [line.strip() for line in raw_text.splitlines() if line.strip()]
    formatted = []

    for index, value in enumerate(values):
        is_last = index == len(values) - 1
        append_delimiter = options.trailing_delimiter or not is_last
        suffix = options.delimiter if append_delimiter else ""
        formatted.append(f"{options.prefix}{value}{options.suffix}{suffix}")

    return "\n".join(formatted)
```

- [ ] **Step 4: Run the full formatter test file**

Run: `set PYTHONPATH=src && python -m unittest tests.test_formatter -v`
Expected: PASS for all formatter tests

- [ ] **Step 5: Commit**

```bash
git add src/text_delimiter_tool/formatter.py tests/test_formatter.py
git commit -m "test: cover formatter edge cases"
```

### Task 4: Build the Tkinter window shell

**Files:**
- Create: `src/text_delimiter_tool/app.py`
- Modify: `run_app.py`

- [ ] **Step 1: Write a failing smoke test by launching the app entry point manually**

Run: `set PYTHONPATH=src && python run_app.py`
Expected: FAIL with import or attribute errors until `text_delimiter_tool.app` exposes `main`

- [ ] **Step 2: Create the minimal Tkinter application shell**

```python
import tkinter as tk
from tkinter import ttk


class TextDelimiterApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Text Delimiter Tool")
        self.root.geometry("1000x600")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = TextDelimiterApp()
    app.run()
```

- [ ] **Step 3: Run the app manually to verify the window opens**

Run: `set PYTHONPATH=src && python run_app.py`
Expected: Window opens with title `Text Delimiter Tool`

- [ ] **Step 4: Commit**

```bash
git add src/text_delimiter_tool/app.py run_app.py
git commit -m "feat: add Tkinter app shell"
```

### Task 5: Add the full UI layout and state variables

**Files:**
- Modify: `src/text_delimiter_tool/app.py`

- [ ] **Step 1: Replace the shell with a two-panel layout and control strip**

```python
import tkinter as tk
from tkinter import ttk

from text_delimiter_tool.formatter import FormatOptions, format_lines


class TextDelimiterApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Text Delimiter Tool")
        self.root.geometry("1000x600")
        self.root.minsize(900, 500)

        self.prefix_var = tk.StringVar(value="")
        self.suffix_var = tk.StringVar(value="")
        self.delimiter_var = tk.StringVar(value=",")
        self.trailing_var = tk.BooleanVar(value=False)

        self._build_layout()
        self._bind_events()
        self.update_output()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        controls = ttk.Frame(self.root, padding=12)
        controls.grid(row=0, column=0, sticky="ew")

        ttk.Label(controls, text="Prefix").grid(row=0, column=0, padx=(0, 6))
        ttk.Entry(controls, textvariable=self.prefix_var, width=8).grid(row=0, column=1, padx=(0, 12))
        ttk.Label(controls, text="Suffix").grid(row=0, column=2, padx=(0, 6))
        ttk.Entry(controls, textvariable=self.suffix_var, width=8).grid(row=0, column=3, padx=(0, 12))
        ttk.Label(controls, text="Delimiter").grid(row=0, column=4, padx=(0, 6))
        ttk.Entry(controls, textvariable=self.delimiter_var, width=8).grid(row=0, column=5, padx=(0, 12))
        ttk.Checkbutton(
            controls,
            text="Add delimiter to every line",
            variable=self.trailing_var,
            command=self.update_output,
        ).grid(row=0, column=6, padx=(0, 12))

        ttk.Button(controls, text="Number + comma", command=self.apply_number_preset).grid(row=0, column=7, padx=4)
        ttk.Button(controls, text="Single quote + comma", command=self.apply_quote_preset).grid(row=0, column=8, padx=4)
        ttk.Button(controls, text="Copy result", command=self.copy_output).grid(row=0, column=9, padx=4)
        ttk.Button(controls, text="Clear", command=self.clear_all).grid(row=0, column=10, padx=4)
        ttk.Button(controls, text="Reset formatting", command=self.reset_formatting).grid(row=0, column=11, padx=4)

        content = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(1, weight=1)

        ttk.Label(content, text="Input").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Label(content, text="Output").grid(row=0, column=1, sticky="w", pady=(0, 6))

        self.input_text = tk.Text(content, wrap="word")
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

        self.output_text = tk.Text(content, wrap="word", state="disabled")
        self.output_text.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
```

- [ ] **Step 2: Run the app to verify the layout renders**

Run: `set PYTHONPATH=src && python run_app.py`
Expected: Window shows control fields, preset buttons, and side-by-side input/output text areas

- [ ] **Step 3: Commit**

```bash
git add src/text_delimiter_tool/app.py
git commit -m "feat: add main app layout"
```

### Task 6: Wire formatting updates and button actions

**Files:**
- Modify: `src/text_delimiter_tool/app.py`

- [ ] **Step 1: Add the remaining app methods and event bindings**

```python
    def _bind_events(self) -> None:
        self.input_text.bind("<<Modified>>", self._handle_input_modified)
        self.prefix_var.trace_add("write", self._handle_option_change)
        self.suffix_var.trace_add("write", self._handle_option_change)
        self.delimiter_var.trace_add("write", self._handle_option_change)

    def _handle_input_modified(self, _event: tk.Event) -> None:
        if self.input_text.edit_modified():
            self.input_text.edit_modified(False)
            self.update_output()

    def _handle_option_change(self, *_args: object) -> None:
        self.update_output()

    def _current_options(self) -> FormatOptions:
        return FormatOptions(
            prefix=self.prefix_var.get(),
            suffix=self.suffix_var.get(),
            delimiter=self.delimiter_var.get(),
            trailing_delimiter=self.trailing_var.get(),
        )

    def update_output(self) -> None:
        formatted = format_lines(self.input_text.get("1.0", "end-1c"), self._current_options())
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", formatted)
        self.output_text.config(state="disabled")

    def apply_number_preset(self) -> None:
        self.prefix_var.set("")
        self.suffix_var.set("")
        self.delimiter_var.set(",")
        self.trailing_var.set(False)
        self.update_output()

    def apply_quote_preset(self) -> None:
        self.prefix_var.set("'")
        self.suffix_var.set("'")
        self.delimiter_var.set(",")
        self.trailing_var.set(False)
        self.update_output()

    def copy_output(self) -> None:
        content = self.output_text.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()

    def clear_all(self) -> None:
        self.input_text.delete("1.0", "end")
        self.update_output()

    def reset_formatting(self) -> None:
        self.apply_number_preset()
```

- [ ] **Step 2: Manually verify live formatting behavior**

Run: `set PYTHONPATH=src && python run_app.py`
Expected:
- Pasting `1`, `2`, `3` on separate lines shows `1,`, `2,`, `3`
- Setting prefix and suffix to `'` shows `'1',`, `'2',`, `'3'`
- Clearing input empties the output
- Copy result places the output on the clipboard

- [ ] **Step 3: Commit**

```bash
git add src/text_delimiter_tool/app.py
git commit -m "feat: wire live formatting interactions"
```

### Task 7: Add the README and final verification

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write a concise README**

```markdown
# Text Delimiter Tool

A small Windows desktop utility for converting pasted multi-line text into delimiter-formatted output.

## Features

- Side-by-side input and output
- Real-time formatting
- Custom prefix, suffix, and delimiter
- Preset buttons for common database formatting patterns
- Copy result to clipboard

## Run

```bash
set PYTHONPATH=src
python run_app.py
```

## Test

```bash
set PYTHONPATH=src
python -m unittest tests.test_formatter -v
```
```

- [ ] **Step 2: Run the formatter tests**

Run: `set PYTHONPATH=src && python -m unittest tests.test_formatter -v`
Expected: PASS for all formatter tests

- [ ] **Step 3: Run the app one more time for manual verification**

Run: `set PYTHONPATH=src && python run_app.py`
Expected: Application window opens and all controls behave as described in the spec

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add usage instructions"
```
