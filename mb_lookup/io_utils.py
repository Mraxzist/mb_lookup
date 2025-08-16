# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Mraxzist

import csv, json
from typing import Dict, List, Optional

from .config import CSV_FIELDS, HEX_RE, I18N, msg, log

def parse_hashes_from_file(path: str) -> List[str]:
    uniq = set()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            for m in HEX_RE.finditer(line):
                uniq.add(m.group(1).lower())
    return sorted(uniq)

def parse_hashes_from_values(values: List[str]) -> List[str]:
    uniq = set()
    for raw in values:
        for m in HEX_RE.finditer(raw):
            uniq.add(m.group(1).lower())
    return sorted(uniq)

def split_values(values: List[str]) -> List[str]:
    out: List[str] = []
    for v in values or []:
        if "," in v:
            parts = [p.strip().strip('"').strip("'") for p in v.split(",")]
            out.extend([p for p in parts if p])
        else:
            out.append(v.strip().strip('"').strip("'"))
    seen, final = set(), []
    for x in out:
        if x and x not in seen:
            seen.add(x)
            final.append(x)
    return final

def search_name_in_export(export_csv: str, name_query: str) -> List[Dict]:
    out = []
    q = (name_query or "").lower()
    with open(export_csv, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = (row.get("file_name") or row.get("filename") or "").lower()
            if q in fname:
                mapped = {
                    "first_seen_utc": row.get("first_seen_utc") or row.get("first_seen") or "",
                    "sha256_hash": row.get("sha256_hash") or row.get("sha256") or "",
                    "md5_hash": row.get("md5_hash") or row.get("md5") or "",
                    "sha1_hash": row.get("sha1_hash") or row.get("sha1") or "",
                    "reporter": row.get("reporter") or "",
                    "file_name": row.get("file_name") or row.get("filename") or "",
                    "file_type_guess": row.get("file_type_guess") or row.get("file_type") or "",
                    "mime_type": row.get("mime_type") or row.get("file_type_mime") or "",
                    "signature": row.get("signature") or "",
                    "clamav": row.get("clamav") or "",
                    "vtpercent": row.get("vtpercent") or "",
                    "imphash": row.get("imphash") or "",
                    "ssdeep": row.get("ssdeep") or "",
                    "tlsh": row.get("tlsh") or "",
                }
                out.append(mapped)
    return out

def write_csv(rows: List[Dict], out_path: Optional[str], lang: str):
    if not out_path:
        return
    if out_path != "-":
        log(msg(lang, "writing_csv") + out_path)
    fout = (open(out_path, "w", newline="", encoding="utf-8") if out_path != "-" else __import__("sys").stdout)
    close = out_path != "-"
    try:
        w = csv.DictWriter(fout, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in CSV_FIELDS})
    finally:
        if close:
            fout.close()

def write_json(rows: List[Dict], json_path: Optional[str], lang: str):
    if not json_path:
        return
    log(msg(lang, "writing_json") + json_path)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
