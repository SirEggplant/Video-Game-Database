"""Terminal table formatter for game search results."""

import shutil
from datetime import date, datetime
from decimal import Decimal
from typing import Any

COLS = [
    ("UUID",          "uuid",    0,  8,  30),
    ("Title",         "text",   10, 10,  28),
    ("Platforms",     "list",    5,  6,  20),
    ("Developers",    "list",    2,  6,  18),
    ("Publishers",    "list",    2,  6,  18),
    ("Playtime",      "minutes", 4,  5,   8),
    ("ESRB",          "text",    3,  4,   6),
    ("User ★",        "rating",  8,  4,   6),
    ("First Release", "date",    3,  8,  10),
    ("Year",          "int",     7,  4,   4),
    ("Min $",         "money",   6,  5,   7),
    ("Max $",         "money",   6,  5,   7),
    ("Genres",        "list",    4,  6,  16),
]
COL_ORDER = [c[0] for c in COLS]


# ----------------------------------------------------------------------
# Value formatters
# ----------------------------------------------------------------------

def _to_str(value: Any) -> str:
    """Return an empty string for None, otherwise str(value)."""
    return "" if value is None else str(value)


def _fmt_list(value: Any) -> str:
    """Format a list/tuple/set or PostgreSQL array literal as a comma-separated string."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_to_str(item) for item in value)
    text = _to_str(value)
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1].replace('"', "")
        return ", ".join(part for part in text.split(",") if part)
    return text


def _fmt_minutes(minutes: Any) -> str:
    """Format an integer number of minutes as 'Xh MMm'."""
    if minutes in (None, ""):
        return ""
    try:
        minutes = int(minutes)
    except (ValueError, TypeError):
        return _to_str(minutes)
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins:02d}m"


def _fmt_rating(rating: Any) -> str:
    """Format a numeric rating with one decimal place."""
    if rating in (None, ""):
        return ""
    try:
        return f"{float(rating):.1f}"
    except (ValueError, TypeError):
        return _to_str(rating)


def _fmt_date(value: Any) -> str:
    """Format a date or datetime as YYYY-MM-DD."""
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return _to_str(value).split(" ")[0]


def _fmt_money(amount: Any) -> str:
    """Format a numeric amount as a dollar value with two decimals."""
    if amount in (None, ""):
        return ""
    try:
        return f"${Decimal(str(amount)):.2f}"
    except (ValueError, TypeError, ArithmeticError):
        return _to_str(amount)


_FORMATTERS = {
    "list": _fmt_list,
    "minutes": _fmt_minutes,
    "rating": _fmt_rating,
    "date": _fmt_date,
    "money": _fmt_money,
    "text": _to_str,
    "uuid": _to_str,
    "int": _to_str,
}


def _clamp(text: str, width: int) -> str:
    """Truncate text to fit within width, appending an ellipsis if cut."""
    return text if len(text) <= width else (text[: max(1, width - 1)] + "…")


# ----------------------------------------------------------------------
# Column selection
# ----------------------------------------------------------------------

def _build_spec(show_uuid: bool, view: str, columns: Any) -> list:
    """Choose which columns to display based on flags."""
    spec = [col for col in COLS if show_uuid or col[0] != "UUID"]
    if columns:
        wanted = set(columns)
        return [col for col in spec if col[0] in wanted]
    if view == "compact":
        keep = {"Title", "User ★", "Year", "Min $", "Genres"}
        return [col for col in spec if col[0] in keep]
    return spec


# ----------------------------------------------------------------------
# Data preparation
# ----------------------------------------------------------------------

def _format_rows(rows: list, col_names: list, kinds: list) -> list:
    """Convert raw DB rows into a 2D list of formatted strings."""
    name_to_idx = {name: i for i, name in enumerate(COL_ORDER)}
    formatters = [_FORMATTERS[kind] for kind in kinds]
    table = []
    for row in rows:
        formatted = []
        for idx, name in enumerate(col_names):
            raw = row[name_to_idx[name]]
            formatted.append(formatters[idx](raw))
        table.append(formatted)
    return table


def _compute_widths(col_names: list, prefs: list, table: list) -> list:
    """Compute initial column widths based on header and data lengths."""
    widths = []
    for i, name in enumerate(col_names):
        longest = max((len(r[i]) for r in table), default=prefs[i])
        widths.append(max(len(name), min(prefs[i], longest)))
    return widths


def _min_widths(col_names: list, mins: list) -> list:
    """Return the minimum allowed width for each column."""
    return [max(mins[i], len(col_names[i])) for i in range(len(col_names))]


# ----------------------------------------------------------------------
# Width fitting
# ----------------------------------------------------------------------

def _total_width(ws: list) -> int:
    """Return the total rendered width of a table with column widths ws."""
    return 3 + sum(ws) + 3 * (len(ws) - 1) + 1


def _shrink_widths(ws: list, min_ws: list, prios: list, term_width: int) -> None:
    """Reduce column widths in low-priority order until the table fits."""
    if _total_width(ws) <= term_width:
        return
    for i in sorted(range(len(ws)), key=lambda idx: prios[idx]):
        while ws[i] > min_ws[i] and _total_width(ws) > term_width:
            ws[i] -= 1


def _drop_columns(
    table: list,
    ws: list,
    min_ws: list,
    prefs: list,
    prios: list,
    kinds: list,
    col_names: list,
    term_width: int,
) -> None:
    """Drop the lowest-priority columns until the table fits the terminal."""
    if _total_width(ws) <= term_width:
        return
    droppable = [
        i
        for i, _ in sorted(enumerate(prios), key=lambda pair: pair[1])
        if col_names[i] != "Title"
    ]
    for i in droppable:
        if _total_width(ws) <= term_width:
            break
        for row in table:
            row.pop(i)
        prios.pop(i)
        ws.pop(i)
        min_ws.pop(i)
        prefs.pop(i)
        kinds.pop(i)
        col_names.pop(i)


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def _render_table(col_names: list, ws: list, table: list) -> None:
    """Print the final formatted table."""
    separator = "+-" + "-+-".join("-" * w for w in ws) + "-+"
    header = " | ".join(
        f"{_clamp(col_names[i], ws[i]):<{ws[i]}}" for i in range(len(ws))
    )
    print(separator)
    print("| " + header + " |")
    print(separator)
    for row in table:
        line = " | ".join(
            f"{_clamp(row[i], ws[i]):<{ws[i]}}" for i in range(len(ws))
        )
        print("| " + line + " |")
    print(separator)


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------

def print_games(
    rows: list,
    *,
    show_uuid: bool = False,
    view: str = "auto",
    columns: Any = None,
) -> None:
    """Print a list of game rows as a formatted terminal table.

    Args:
        rows: A list of 13-element tuples (matching the game_listing view).
        show_uuid: Include the UUID column.
        view: 'auto' for all columns, 'compact' for a smaller set.
        columns: Optional explicit list of column names to include.
    """
    if not rows:
        print("No games found.")
        return
    if len(rows[0]) != 13:
        raise ValueError(f"Expected 13 columns, got {len(rows[0])}.")

    spec = _build_spec(show_uuid, view, columns)
    col_names = [col[0] for col in spec]
    kinds = [col[1] for col in spec]
    mins = [col[3] for col in spec]
    prefs = [col[4] for col in spec]
    prios = [col[2] for col in spec]

    table = _format_rows(rows, col_names, kinds)
    widths = _compute_widths(col_names, prefs, table)
    min_ws = _min_widths(col_names, mins)

    term_width = shutil.get_terminal_size((100, 24)).columns
    _shrink_widths(widths, min_ws, prios, term_width)
    _drop_columns(table, widths, min_ws, prefs, prios, kinds, col_names, term_width)

    _render_table(col_names, widths, table)
    