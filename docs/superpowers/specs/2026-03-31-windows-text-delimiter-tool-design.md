# Windows Text Delimiter Tool Design

## Overview

This project is a local Windows desktop utility for transforming pasted multi-line text into delimiter-formatted output. The first version focuses on a single-window workflow for data copied from database query results or spreadsheets, where each input line represents one value.

Example input:

```text
1
2
3
```

Example outputs:

```text
1,
2,
3
```

```text
'1',
'2',
'3'
```

## Goals

- Run locally on Windows as a lightweight desktop tool
- Let the user paste multi-line text on the left and see transformed output on the right
- Support fixed presets plus customizable prefix, suffix, and delimiter values
- Trim leading and trailing whitespace from each line
- Ignore empty lines
- Update output in real time as the input or formatting options change

## Non-Goals

The first version does not include:

- Clipboard monitoring
- Automatic paste into external applications
- File import or export
- Saved custom templates
- Full SQL statement generation such as `IN (...)`
- Sorting, deduplication, or batch replacement logic
- Content validation by data type

## Target Platform

- Windows desktop
- Local-only execution
- Recommended implementation: Python with Tkinter

Python with Tkinter is the preferred choice because it keeps the first version small, fast to build, and easy to distribute for a utility-style desktop app.

## User Workflow

1. Launch the application.
2. Paste raw multi-line text into the left input panel.
3. Optionally click a preset to fill common formatting values.
4. Adjust prefix, suffix, delimiter, and trailing-delimiter behavior if needed.
5. View the transformed result in the right output panel immediately.
6. Copy the result for use in SQL, scripts, or other tools.

## UI Design

The first version uses a single main window with three areas:

### Input Panel

- Large text area on the left
- Accepts pasted multi-line plain text
- Source content is treated as one item per line

### Formatting Panel

- A compact control area above or between the text panels
- Inputs for:
  - Prefix
  - Suffix
  - Delimiter
- Checkbox for:
  - Add delimiter to the end of every output line
- Preset buttons for:
  - Number + comma
  - Single quote + comma
- Utility buttons for:
  - Copy result
  - Clear
  - Reset formatting

### Output Panel

- Large read-only text area on the right
- Shows the transformed output in real time
- Allows selecting and copying generated text

## Data Processing Rules

Input is processed line by line using the following rules:

1. Split the input by line.
2. Trim leading and trailing whitespace from each line.
3. Remove empty lines after trimming.
4. Preserve the original order of remaining lines.
5. For each remaining line, generate:

```text
prefix + value + suffix + optional delimiter
```

The optional delimiter behavior is controlled by a checkbox:

- Enabled: every generated line ends with the delimiter
- Disabled: only lines before the last line end with the delimiter

## Example Transformations

### Preset: Number + Comma

Settings:

- Prefix: empty
- Suffix: empty
- Delimiter: `,`
- Add delimiter to every line: disabled

Input:

```text
1
2
3
```

Output:

```text
1,
2,
3
```

### Preset: Single Quote + Comma

Settings:

- Prefix: `'`
- Suffix: `'`
- Delimiter: `,`
- Add delimiter to every line: enabled

Input:

```text
1
2
3
```

Output:

```text
'1',
'2',
'3',
```

If the user wants:

```text
'1',
'2',
'3'
```

they can disable the trailing-delimiter checkbox.

## Error Handling

The first version keeps error handling minimal and predictable:

- Empty input produces empty output
- Empty prefix, suffix, or delimiter fields are valid
- All values are treated as plain text
- No numeric or SQL validation is performed
- Invalid formatting combinations do not raise errors; they simply produce the direct text result implied by the current settings

## Architecture

The implementation should be split into focused parts:

- A Tkinter application entry point that creates the window
- A small formatting engine responsible only for text transformation
- UI event bindings that trigger recomputation when input or controls change

This separation keeps the formatting logic testable without the GUI and keeps the first version easy to extend.

## Testing Strategy

The formatting engine should be covered with automated tests. The GUI can remain lightly tested in the first version, with manual verification for layout and interaction.

Core test cases:

- Basic comma formatting
- Single-quote wrapping
- Leading and trailing whitespace trimming
- Empty line removal
- Trailing delimiter enabled
- Trailing delimiter disabled
- Empty input
- Empty delimiter
- Empty prefix and suffix

## Future Extensions

Possible later additions:

- More built-in presets
- SQL helper templates
- Clipboard watcher mode
- Export to file
- Custom preset persistence
- Duplicate removal and sorting options
