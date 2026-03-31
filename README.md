# Text Delimiter Tool

Version: see `VERSION`

A lightweight Windows desktop utility for converting pasted multi-line text into delimiter-ready output.

## What It Does

This tool is built for the common workflow of copying a single column of values from a database query, spreadsheet, or other tabular source and turning it into reusable formatted text.

Example input:

```text
1
2
3
```

Example output:

```text
'1',
'2',
'3'
```

## Features

- Side-by-side input and output
- Real-time formatting
- Custom prefix, suffix, and delimiter
- Preset buttons for common database formatting patterns
- Copy result to clipboard
- Keyboard shortcuts for copy and clear
- Custom About window
- Windows icon and packaging support

## Project Structure

```text
src/text_delimiter_tool/
  app.py               Tkinter desktop UI
  formatter.py         Pure formatting logic
  version.py           App name and version loading
assets/
  app.png              Window icon asset
  app.ico              Windows executable icon
scripts/
  build.ps1            Windows packaging script
VERSION                Single source of truth for versioning
run_app.py             Local application entry point
README.md              Project overview and usage
```

## Run Locally

```powershell
python run_app.py
```

## Test

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_formatter -v
python -m unittest tests.test_version -v
```

## Keyboard Shortcuts

- `Ctrl+Enter`: copy formatted result
- `Ctrl+L`: clear input and keep focus in the source editor

## Versioning

`VERSION` is the single source of truth.

- The desktop app reads its displayed version from `VERSION`
- The Windows packaging script reads the same `VERSION` file
- When you release a new version, change `VERSION` only

## Build And Release

### Prerequisites

- Windows PowerShell
- Python 3.13 or later
- `pyinstaller` installed in the selected Python environment

Install packaging dependency:

```powershell
python -m pip install pyinstaller
```

### Local Verification Before Packaging

Run both test modules before building:

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_formatter -v
python -m unittest tests.test_version -v
```

### Build EXE

Recommended clean build:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Clean
```

Build output:

```text
dist\TextDelimiterTool.exe
```

### Standard Release Flow

1. Update `VERSION`.
2. Run local tests.
3. Build with `-Clean`.
4. Manually launch `dist\TextDelimiterTool.exe` once on the build machine.
5. Replace any previously distributed old `exe` with the newly built file.

### Build Script Notes

- `assets\app.ico` is used automatically when present
- Windows file metadata is generated from `VERSION`
- The build script bundles `VERSION` into the PyInstaller package
- The app reads version metadata from bundled runtime data first, then falls back to development paths

Examples:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Clean
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Python py
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Name MyDelimiterTool
```

### Troubleshooting

If a packaged `exe` fails immediately on startup, first confirm you are not launching an older build.

Previous broken packages could fail with an error similar to:

```text
FileNotFoundError: ... Temp\VERSION
```

That failure means the old package was built without bundling the `VERSION` file. Rebuild with the current `scripts\build.ps1` and redistribute the newly generated `dist\TextDelimiterTool.exe`.

If packaging fails:

- Confirm `python -m PyInstaller --version` works
- Confirm `VERSION` exists and uses `major.minor.patch`, for example `1.0.0`
- Confirm `assets\app.ico` exists if you expect a custom icon

## Maintenance Rules

- Keep source files in `src/`
- Keep icons and visual assets in `assets/`
- Keep build and automation scripts in `scripts/`
- Do not commit generated artifacts from `build/`, `dist/`, `__pycache__/`, or `*.spec`
- If you change the version, update `VERSION` only

## Current Scope

This project intentionally stays focused on local text formatting.

Included:

- Multi-line input formatting
- Preset formatting buttons
- Copy and clear workflow
- Windows packaging support

Not included:

- Clipboard monitoring
- File import/export
- SQL statement generation beyond line formatting
- Template persistence
- Sorting, deduplication, or data validation
