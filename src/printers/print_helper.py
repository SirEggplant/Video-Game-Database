import shutil
from datetime import date, datetime
from decimal import Decimal

# ---- FIX: define COLS first ----
COLS = [
    ("UUID",           "uuid",    0,  8,  30),
    ("Title",          "text",   10, 10,  28),
    ("Platforms",      "list",    5,  6,  20),
    ("Developers",     "list",    2,  6,  18),
    ("Publishers",     "list",    2,  6,  18),
    ("Playtime",       "minutes", 4,  5,   8),
    ("ESRB",           "text",    3,  4,   6),
    ("User ★",         "rating",  8,  4,   6),
    ("First Release",  "date",    3,  8,  10),
    ("Year",           "int",     7,  4,   4),
    ("Min $",          "money",   6,  5,   7),
    ("Max $",          "money",   6,  5,   7),
    ("Genres",         "list",    4,  6,  16),
]
COL_ORDER = [c[0] for c in COLS]  # now defined properly

# ---- helpers ----
def _to_str(x): return "" if x is None else str(x)

def _fmt_list(x):
    if x is None: return ""
    if isinstance(x, (list, tuple, set)):
        return ", ".join(_to_str(i) for i in x)
    s = _to_str(x)
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1].replace('"', '')
        return ", ".join(part for part in s.split(",") if part)
    return s

def _fmt_minutes(m):
    if m in (None, ""): return ""
    try: m = int(m)
    except: return _to_str(m)
    h, mm = divmod(m, 60)
    return f"{h}h {mm:02d}m"

def _fmt_rating(r):
    if r in (None, ""): return ""
    try: return f"{float(r):.1f}"
    except: return _to_str(r)

def _fmt_date(d):
    if d is None: return ""
    if isinstance(d, (date, datetime)): return d.strftime("%Y-%m-%d")
    return _to_str(d).split(" ")[0]

def _fmt_money(x):
    if x in (None, ""): return ""
    try: return f"${Decimal(str(x)):.2f}"
    except: return _to_str(x)

_FORMATTERS = {
    "list": _fmt_list, "minutes": _fmt_minutes, "rating": _fmt_rating,
    "date": _fmt_date, "money": _fmt_money, "text": _to_str, "uuid": _to_str, "int": _to_str
}

def _clamp(s, w): return s if len(s) <= w else (s[:max(1, w-1)] + "…")

# ---- main function ----
def print_games(rows, *, show_uuid=False, view="auto", columns=None):
    if not rows:
        print("No games found.")
        return
    if len(rows[0]) != 13:
        raise ValueError(f"Expected 13 columns, got {len(rows[0])}.")

    # Build base spec
    spec = [c for c in COLS if (show_uuid or c[0] != "UUID")]
    if columns:
        want = set(columns)
        spec = [c for c in spec if c[0] in want]
    elif view == "compact":
        keep = {"Title", "User ★", "Year", "Min $", "Genres"}
        spec = [c for c in spec if c[0] in keep]
    # else: auto/wide keep spec as-is

    # Prepare data strings per column
    name_to_idx = {name: i for i, name in enumerate(COL_ORDER)}
    col_names = [name for (name, *_rest) in spec]
    kinds     = [kind for (_n, kind, *_r) in spec]
    mins      = [mn  for (_n, _k, _p, mn, _pw) in spec]
    prefs     = [pw  for (_n, _k, _p, _mn, pw) in spec]
    prios     = [pr  for (_n, _k, pr, _mn, _pw) in spec]

    fmt = [_FORMATTERS[k] for k in kinds]
    table = []
    for r in rows:
        vals = []
        for i, name in enumerate(col_names):
            raw = r[name_to_idx[name]]
            vals.append(fmt[i](raw))
        table.append(vals)

    # Compute widths
    widths = [max(len(col_names[i]), min(prefs[i], max((len(row[i]) for row in table), default=prefs[i]))) for i in range(len(col_names))]
    minw   = [max(mins[i], len(col_names[i])) for i in range(len(col_names))]

    term_w = shutil.get_terminal_size((100, 24)).columns
    def total_width(ws): return 3 + sum(ws) + 3*(len(ws)-1) + 1

    ws = widths[:]

    # shrink columns
    if total_width(ws) > term_w:
        order = sorted(range(len(ws)), key=lambda i: prios[i])
        for i in order:
            while ws[i] > minw[i] and total_width(ws) > term_w:
                ws[i] -= 1

    # drop columns if needed
    if total_width(ws) > term_w:
        droppable = [i for i,_ in sorted(enumerate(prios), key=lambda t: t[1]) if col_names[i] != "Title"]
        for i in droppable:
            for row in table: row.pop(i)
            prios.pop(i); ws.pop(i); minw.pop(i); prefs.pop(i); kinds.pop(i); col_names.pop(i)
            if total_width(ws) <= term_w: break

    sep = "+-" + "-+-".join("-"*w for w in ws) + "-+"
    print(sep)
    print("| " + " | ".join(f"{_clamp(col_names[i], ws[i]):<{ws[i]}}" for i in range(len(ws))) + " |")
    print(sep)
    for row in table:
        print("| " + " | ".join(f"{_clamp(row[i], ws[i]):<{ws[i]}}" for i in range(len(ws))) + " |")
    print(sep)
