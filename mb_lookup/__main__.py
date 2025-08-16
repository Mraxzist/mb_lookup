# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Mraxzist

import argparse
from typing import Dict, List, Optional

from .version import VERSION, USER_AGENT
from .config import I18N, msg, log, CSV_FIELDS, API_KEY_DEFAULT
from .api import build_session
from .core import get_info_by_hashes, get_by_signature, get_recent, filter_by_name
from .io_utils import (
    parse_hashes_from_file, parse_hashes_from_values, split_values,
    search_name_in_export, write_csv, write_json
)
from .preview import live_init, live_emit_row, LiveCtx

def resolve_api_key(cli_key: Optional[str]) -> Optional[str]:
    if cli_key:
        return cli_key
    if API_KEY_DEFAULT and API_KEY_DEFAULT != "PUT-YOUR-API-KEY-HERE":
        return API_KEY_DEFAULT
    return None

def main():
    ap = argparse.ArgumentParser(description=f"MalwareBazaar bulk lookup (v{VERSION})")
    ap.add_argument("-i","--input", help="Path to TXT file with queries (hashes/signatures/names). Optional with --values.")
    ap.add_argument("-m","--mode", required=True, choices=["hash","signature","name"], help="Lookup mode.")
    ap.add_argument("--values", nargs="*", help="Inline values (hashes/signatures/names). Comma or space separated.")
    ap.add_argument("--api-key", help="API key (or put it into API_KEY_DEFAULT in the script).")
    ap.add_argument("--lang", choices=["en","ru"], default="en", help="Localization for logs.")
    ap.add_argument("-o","--out", default="-", help="CSV output path (default: stdout). Use '-' for stdout.")
    ap.add_argument("--json-out", help="JSON output path (array of objects with selected fields).")
    ap.add_argument("--limit", type=int, default=200, help="Limit for signature mode (<=1000).")
    ap.add_argument("--recent-selector", default="100", choices=["time","100"],
                    help="For name mode without export: 'time' (last hour) or '100' (last 100).")
    ap.add_argument("--export-csv", help="Path to local CSV export (Full data dump) for name mode to search entire DB.")
    # networking
    ap.add_argument("--connect-timeout", type=float, default=10.0, help="Connect timeout, seconds.")
    ap.add_argument("--read-timeout", type=float, default=45.0, help="Read timeout, seconds.")
    ap.add_argument("--retries", type=int, default=3, help="HTTP retries on 429/5xx.")
    ap.add_argument("--backoff", type=float, default=1.0, help="Retry backoff factor.")
    ap.add_argument("--proxy", help="HTTP/HTTPS proxy URL, e.g. http://127.0.0.1:8080")
    ap.add_argument("--verify", action="store_true", default=True, help="Verify TLS certificates (default: True).")
    ap.add_argument("--no-verify", action="store_false", dest="verify", help="Disable TLS verification (NOT recommended).")
    # live/preview/progress
    ap.add_argument("--live", dest="live", action="store_true", default=True, help="Print results as they arrive (default).")
    ap.add_argument("--no-live", dest="live", action="store_false", help="Disable live streaming; show final preview only.")
    ap.add_argument("--preview", dest="preview_mode", choices=["none","table","ndjson","csv"], default="table",
                    help="Console preview mode (default: table).")
    ap.add_argument("--progress-interval", type=int, default=25, help="Print processed counter every N items.")

    args = ap.parse_args()
    lang = args.lang

    api_key = resolve_api_key(args.api_key)
    if not api_key:
        import sys
        sys.exit(msg(lang, "need_api"))

    session = build_session(retries=args.retries, backoff=args.backoff, proxy=args.proxy)

    # input
    values: List[str] = split_values(args.values or [])
    file_lines: List[str] = []
    if args.input:
        log(msg(lang, "reading_file") + args.input)
        with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
            file_lines = [ln.strip() for ln in f if ln.strip()]

    results: List[Dict] = []
    live_ctx: Optional[LiveCtx] = None
    if args.live and args.preview_mode != "none":
        live_ctx = live_init(args.preview_mode, args.out, lang)

    try:
        if args.mode == "hash":
            log(msg(lang, "mode_hash"))
            hashes = set(parse_hashes_from_values(values))
            if args.input:
                hashes.update(parse_hashes_from_file(args.input))
            hashes = sorted(hashes)
            if not hashes:
                import sys
                sys.exit(msg(lang, "no_hashes"))
            results.extend(get_info_by_hashes(
                session, hashes, api_key, lang,
                args.connect_timeout, args.read_timeout, args.verify,
                live_ctx, args.progress_interval
            ))

        elif args.mode == "signature":
            log(msg(lang, "mode_sig"))
            sigs = [*values, *file_lines]
            results.extend(get_by_signature(
                session, sigs, api_key, args.limit, lang,
                args.connect_timeout, args.read_timeout, args.verify,
                live_ctx, args.progress_interval
            ))

        elif args.mode == "name":
            log(msg(lang, "mode_name"))
            names = [*(v for v in values if v), *file_lines]
            if args.export_csv:
                from .io_utils import search_name_in_export
                for nm in names:
                    for row in search_name_in_export(args.export_csv, nm):
                        results.append(row)
                        if live_ctx: live_emit_row(live_ctx, row)
            else:
                recent = get_recent(session, api_key, args.recent_selector, lang,
                                    args.connect_timeout, args.read_timeout, args.verify)
                for nm in names:
                    for r in filter(lambda x: nm.lower() in (x.get("file_name","").lower()), recent):
                        results.append(r)
                        if live_ctx: live_emit_row(live_ctx, r)
    except KeyboardInterrupt:
        log(msg(lang, "interrupted"))

    # dedup
    seen = set()
    uniq: List[Dict] = []
    for r in results:
        key = (r.get("sha256_hash",""), r.get("file_name",""))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)

    # финальная статистика
    log(msg(lang, "found_n").format(n=len(uniq)))
    # запись файлов
    write_json(uniq, args.json_out, lang)
    write_csv(uniq, args.out, lang)

if __name__ == "__main__":
    main()
