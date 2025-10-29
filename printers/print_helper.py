

# AI print_games function (updated for game_listing view output)
def print_games(rows):
    """
    Supports new shape (from game_listing-based SELECT):
      0: game_uuid
      1: title
      2: platforms (array)
      3: developers (array)
      4: publishers (array)
      5: total_playtime_minutes (int)
      6: esrb_rating
      7: total_user_rating (float)
      8: first_release_date (date)
      9: released_year (int)
      10: min_price (numeric)
      11: max_price (numeric)
      12: genres (array)
    Falls back to the old shape if detected.
    """
    if not rows:
        print("No games found.")
        return
    if isinstance(rows, tuple):
        rows = [rows]

    # Helpers
    def fmt_list(x, max_items=3):
        if x is None:
            return "-"
        try:
            arr = list(x)
        except Exception:
            return str(x)
        if not arr:
            return "-"
        if len(arr) <= max_items:
            return ", ".join(str(i) for i in arr)
        return ", ".join(str(i) for i in arr[:max_items]) + "…"

    def fmt_hhmm(minutes):
        try:
            m = int(minutes or 0)
        except Exception:
            m = 0
        h = m // 60
        mm = m % 60
        return f"{h:02d}:{mm:02d}"

    def fmt_price(lo, hi):
        try:
            lo = float(lo) if lo is not None else None
        except Exception:
            lo = None
        try:
            hi = float(hi) if hi is not None else None
        except Exception:
            hi = None
        if lo is None and hi is None:
            return "-"
        if lo is None:
            return f"${hi:.2f}"
        if hi is None or abs(hi - lo) < 1e-9:
            return f"${lo:.2f}"
        return f"${lo:.2f}–${hi:.2f}"

    def short_id(uid):
        s = str(uid)
        return s[:8] if len(s) > 8 else s

    # Detect row shape (new vs old)
    new_shape = len(rows[0]) >= 13

    processed = []
    if new_shape:
        # New order from view-backed queries
        for r in rows:
            gid          = r[0]
            title        = r[1]
            platforms    = fmt_list(r[2])
            developers   = fmt_list(r[3])
            publishers   = fmt_list(r[4])
            playtime     = fmt_hhmm(r[5])
            esrb         = r[6]
            user_rating  = f"{float(r[7]):.1f}" if r[7] is not None else "-"
            released     = str(r[9]) if r[9] is not None else (str(r[8]) if r[8] else "-")
            price        = fmt_price(r[10], r[11])
            processed.append((
                title or "",
                platforms,
                developers,
                publishers,
                esrb or "",
                user_rating,
                playtime,
                released,
                price,
                short_id(gid),
            ))
    else:
        # Old shape fallback: 0 id, 1 title, 2 desc, 3 total_user_rating, 4 esrb, 5 players
        for r in rows:
            gid          = r[0]
            title        = r[1]
            esrb         = r[4] if len(r) > 4 else ""
            user_rating  = f"{float(r[3]):.1f}" if len(r) > 3 and r[3] is not None else "-"
            processed.append((
                title or "",
                "-", "-", "-",                # platforms, developers, publishers (unknown)
                esrb or "",
                user_rating,
                "00:00",                      # no playtime in old shape
                "-",                          # released
                "-",                          # price
                short_id(gid),
            ))

    headers = ["Title", "Platforms", "Developers", "Publishers", "ESRB", "User★", "Playtime", "Released", "Price", "ID"]

    # Column widths
    col_w = [len(h) for h in headers]
    for row in processed:
        for i, val in enumerate(row):
            col_w[i] = max(col_w[i], len(str(val)))

    # Build separator
    sep = "+-" + "-+-".join("-"*w for w in col_w) + "-+"

    # Print table
    print(sep)
    print("| " + " | ".join(f"{headers[i]:<{col_w[i]}}" for i in range(len(headers))) + " |")
    print(sep)
    for row in processed:
        print("| " + " | ".join(f"{str(row[i]):<{col_w[i]}}" for i in range(len(headers))) + " |")
    print(sep)
