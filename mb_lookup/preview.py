# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Mraxzist

import csv, json, sys
from dataclasses import dataclass
from typing import Dict, List, Optional

from .config import CSV_FIELDS, I18N, msg

def _truncate(s: str, maxw: int) -> str:
    s = "" if s is None else str(s)
    return s if len(s) <= maxw else s[:maxw-1] + "…"

def choose_print_stream(out_path: str):
    return sys.stderr if out_path == "-" else sys.stdout

@dataclass
class LiveCtx:
    mode: str
    stream: any
    header: bool
    rows: int
    csvw: Optional[csv.DictWriter]
    cols: Optional[List] = None

def live_init(preview_mode: str, out_path: str, lang: str) -> LiveCtx:
    stream = choose_print_stream(out_path)
    ctx = LiveCtx(mode=preview_mode, stream=stream, header=False, rows=0, csvw=None, cols=None)
    if preview_mode == "table":
        labels = I18N.get(lang, I18N["en"])["cols"]
        ctx.cols = [
            ("first_seen_utc", labels["first_seen_utc"], 19),
            ("sha256_hash",    labels["sha256_hash"],    12),
            ("file_name",      labels["file_name"],      36),
            ("signature",      labels["signature"],      18),
            ("vtpercent",      labels["vtpercent"],       5),
        ]
        header = "  ".join(_truncate(h, w).ljust(w) for _, h, w in ctx.cols)
        print(msg(lang, "streaming"), file=stream, flush=True)
        print(header, file=stream, flush=True)
        print("-" * len(header), file=stream, flush=True)
        ctx.header = True
    elif preview_mode == "csv":
        csvw = csv.DictWriter(stream, fieldnames=CSV_FIELDS, extrasaction="ignore")
        csvw.writeheader()
        ctx.csvw = csvw
        ctx.header = True
    elif preview_mode == "ndjson":
        print(msg(lang, "streaming"), file=stream, flush=True)
    return ctx

def live_emit_row(ctx: LiveCtx, row: Dict):
    mode = ctx.mode
    st = ctx.stream
    if mode == "table":
        vals = dict(row)
        vals["sha256_hash"] = (vals.get("sha256_hash","")[:12])
        line = "  ".join(_truncate(vals.get(k, ""), w).ljust(w) for k, _, w in ctx.cols)
        print(line, file=st, flush=True)
    elif mode == "ndjson":
        print(json.dumps(row, ensure_ascii=False), file=st, flush=True)
    elif mode == "csv":
        ctx.csvw.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in CSV_FIELDS})
        st.flush()
    ctx.rows += 1
