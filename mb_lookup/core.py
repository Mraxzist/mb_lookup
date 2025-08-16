# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Mraxzist

from typing import Dict, Iterable, List, Optional

from .api import request_api
from .config import CSV_FIELDS, I18N
from .config import msg
from .preview import LiveCtx, live_emit_row

def normalize_item(it: Dict) -> Dict:
    intel = it.get("intelligence") or {}
    clam = it.get("clamav")
    if clam is None:
        clam = intel.get("clamav")
    if isinstance(clam, list):
        clam = ";".join(str(x) for x in clam)
    vtpercent = it.get("vtpercent")
    if vtpercent is None and isinstance(intel, dict):
        vt = intel.get("virustotal")
        if isinstance(vt, dict):
            vtpercent = vt.get("percent") or vt.get("vtpercent")
    return {
        "first_seen_utc": it.get("first_seen") or it.get("first_seen_utc") or "",
        "sha256_hash": it.get("sha256_hash") or "",
        "md5_hash": it.get("md5_hash") or "",
        "sha1_hash": it.get("sha1_hash") or "",
        "reporter": it.get("reporter") or "",
        "file_name": it.get("file_name") or "",
        "file_type_guess": it.get("file_type") or it.get("file_type_guess") or "",
        "mime_type": it.get("file_type_mime") or it.get("mime_type") or "",
        "signature": it.get("signature") or "",
        "clamav": clam or "",
        "vtpercent": "" if vtpercent is None else str(vtpercent),
        "imphash": it.get("imphash") or "",
        "ssdeep": it.get("ssdeep") or "",
        "tlsh": it.get("tlsh") or "",
    }

def get_info_by_hashes(
    session, hashes: Iterable[str], api_key: str, lang: str,
    connect_timeout: float, read_timeout: float, verify_tls: bool,
    live_ctx: Optional[LiveCtx], progress_interval: int
) -> List[Dict]:
    rows: List[Dict] = []
    total = len(list(hashes)) if not isinstance(hashes, list) else len(hashes)
    if not isinstance(hashes, list):
        hashes = list(hashes)
    for i, h in enumerate(hashes, 1):
        resp = request_api(session, {"query": "get_info", "hash": h}, api_key, lang,
                           connect_timeout, read_timeout, verify_tls)
        if resp.get("query_status") in {"hash_not_found","no_results"}:
            if progress_interval and (i % progress_interval == 0):
                from .config import log
                log(msg(lang, "processed").format(i=i, n=total))
            continue
        for it in resp.get("data", []) or []:
            row = normalize_item(it)
            rows.append(row)
            if live_ctx:
                live_emit_row(live_ctx, row)
        if progress_interval and (i % progress_interval == 0):
            from .config import log
            log(msg(lang, "processed").format(i=i, n=total))
    return rows

def get_by_signature(
    session, sigs: Iterable[str], api_key: str, limit: int, lang: str,
    connect_timeout: float, read_timeout: float, verify_tls: bool,
    live_ctx: Optional[LiveCtx], progress_interval: int
) -> List[Dict]:
    out: List[Dict] = []
    sigs = [s for s in sigs if s]
    total = len(sigs)
    for i, sig in enumerate(sigs, 1):
        resp = request_api(session, {"query": "get_siginfo", "signature": sig, "limit": str(min(limit, 1000))},
                           api_key, lang, connect_timeout, read_timeout, verify_tls)
        if resp.get("query_status") in {"signature_not_found","no_results"}:
            if progress_interval and (i % progress_interval == 0):
                from .config import log
                log(msg(lang, "processed").format(i=i, n=total))
            continue
        for it in resp.get("data", []) or []:
            row = normalize_item(it)
            out.append(row)
            if live_ctx:
                live_emit_row(live_ctx, row)
        if progress_interval and (i % progress_interval == 0):
            from .config import log
            log(msg(lang, "processed").format(i=i, n=total))
    return out

def get_recent(session, api_key: str, selector: str, lang: str,
               connect_timeout: float, read_timeout: float, verify_tls: bool) -> List[Dict]:
    resp = request_api(session, {"query":"get_recent","selector":selector}, api_key, lang,
                       connect_timeout, read_timeout, verify_tls)
    if resp.get("query_status") in {"no_results"}:
        return []
    return [normalize_item(it) for it in (resp.get("data", []) or [])]

def filter_by_name(rows: List[Dict], name_query: str) -> List[Dict]:
    q = (name_query or "").lower()
    return [r for r in rows if q in (r.get("file_name","").lower())]
