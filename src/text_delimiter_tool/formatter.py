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
