# mb-lookup — MalwareBazaar bulk lookup (CLI + mini-SDK) 🚀

**English** | [Русский](README.ru.md)

## 🎯 Purpose

`mb_lookup` is a tool for **indicator enrichment** and **fast artifact triage** against the [MalwareBazaar](https://bazaar.abuse.ch/) repository in TI/DFIR/SOC workflows.  
It helps you quickly learn **what a file is**, when it was **first seen**, which **family/signature** it belongs to, and gather useful attributes (MIME, ClamAV, VT%, imphash, ssdeep, tlsh, etc.) — **without downloading or executing** samples.

### Where it helps
- 🕵️ **DFIR / Incident Response:** quick enrichment of hashes / file artifacts from tickets or dumps.
- 🛡️ **SOC triage:** checking whether attachments/binaries are “known” by hash or family.
- 🧪 **Malware research:** assembling corpora by signature/family for offline analysis.
- 🔍 **Hunting / Threat Intel:** pivoting by `first_seen_utc` and by related families/signatures.

### What it does
- 🔑 **Hash lookups** (`MD5/SHA1/SHA256`) via `get_info`.
- 🧬 **Signature/family lookups** via `get_siginfo` (up to the latest 1000).
- 📄 **Filename lookups** — MalwareBazaar has no native filename search API, so this tool:
  - uses a **“recent” filter** (last 100 or last hour), and/or
  - an **offline search** in the **full CSV export** (local file).

### What the tool **does not** do
- ⛔ **Does not download or execute** malicious samples.
- ⛔ **Does not bypass** abuse.ch limits/policy; it is **not** an antivirus or sandbox.
- ⛔ **Does not guarantee** all attributes are present in every record (many are optional upstream).
- ⛔ **Does not guarantee** that a hash **not** found in the database implies the file is benign.

### Limits & caveats
- 📉 **API limits:** you may hit `HTTP 429` and see `X-RateLimit-*` headers. The tool surfaces friendly warnings and supports backoff/retries.
- 🔠 **Filename search** is heuristic (recent) or offline (CSV dump); full coverage is possible only with the CSV export.
- 🌐 Corporate networks with proxies/TLS interception may require `--proxy` and/or `--no-verify`.

### Disclaimer ⚠️
This tool is for **legitimate research, education, and defense** (DFIR/SOC/TI) only, within applicable law and local policies.  
You are solely responsible for any **downloading/handling/execution** of samples and for complying with all legal and licensing requirements. The authors/contributors assume no liability.

## ✨ Features

* **Lookups**

  * `hash` → `get_info` (MD5/SHA1/SHA256 mixed, any order)
  * `signature` → `get_siginfo` (family/signature)
  * `name` → filter by filename in **Recent** or via **local CSV export** (offline)
* **Inputs**: from file (`-i`) and/or inline via `--values "a,b" c d`
* **Outputs**: CSV (`-o out.csv`) and/or JSON (`--json-out out.json`)
* **Live console preview** while running: `table` | `ndjson` | `csv` | `none` 👀
* **Rate-limit aware & resilient**: retries, backoff, timeouts, proxy, TLS verify toggle
* **Bilingual logs**: `--lang en|ru`

---

## 🧱 Project layout

```
mb_lookup/
├─ __init__.py
├─ __main__.py         # module entrypoint: python -m mb_lookup
├─ api.py              # HTTP session, retries, request_api, rate-limit notices
├─ config.py           # constants, i18n, logging helpers
├─ core.py             # normalize_item, get_info_by_hashes, get_by_signature, …
├─ io_utils.py         # parsing, CSV/JSON writers, CSV export search
├─ preview.py          # live preview printers (table/ndjson/csv)
└─ version.py          # version, user-agent
requirements.txt
```

---

## ⚙️ Install

```bash
git clone https://github.com/Mraxzist/mb_lookup.git
cd mb_lookup
python -m pip install -r requirements.txt
```

## ❓ What is this and how do I run it?

**Runs as a Python module:**  
```bash
python -m mb_lookup [options]
```

> Optional (developer nicety): add a `pyproject.toml` with a console entry point so you can run `mb_lookup …`.

---

## 🔐 API key

Either edit `mb_lookup/config.py`:

```python
API_KEY_DEFAULT = "YOUR-API-KEY"
```

…or pass it on the CLI:

```bash
--api-key YOUR-API-KEY
```

## 🏃 Quick start

Hash lookups from a file, live table preview, save CSV + JSON:

```bash
python -m mb_lookup -i sha256.txt --mode hash --api-key YOUR-KEY --lang en --preview table --live -o out.csv --json-out out.json
```

You’ll see rows as they are found, plus progress logs. ✅

---

## 🛠 CLI usage

Show all options:

```bash
python -m mb_lookup -h
```

**Core options**

| Option        | Description                                                           |
| ------------- | --------------------------------------------------------------------- |
| `-m, --mode`  | `hash` \| `signature` \| `name`                                       |
| `-i, --input` | TXT with queries (hashes/signatures/names)                            |
| `--values`    | Inline queries (space or comma separated), e.g. `--values "h1,h2" h3` |
| `--api-key`   | API key (or set `API_KEY_DEFAULT` in `config.py`)                     |
| `--lang`      | Log language: `en` (default) or `ru`                                  |
| `-o, --out`   | CSV output path (use `-` for stdout)                                  |
| `--json-out`  | JSON output path (array of objects)                                   |

**Mode-specific**

* `--limit` (signature): max results per signature (≤ 1000)
* `--recent-selector` (name): `time` (last hour) or `100` (last 100)
* `--export-csv` (name): path to MalwareBazaar full CSV export for offline filename search

**Networking & resilience**

* `--connect-timeout` (default 10s), `--read-timeout` (default 45s)
* `--retries` (default 3), `--backoff` (default 1.0)
* `--proxy http://127.0.0.1:8080`
* `--verify` / `--no-verify` (TLS)

**Console preview & progress**

* `--live` / `--no-live` — stream results while running (default: `--live`)
* `--preview table|ndjson|csv|none` (default: `table`)
* `--progress-interval 25` — print **Processed X/Y** every N items

---

## 📚 Examples

**1) Hash lookups (file + live)**

```bash
python -m mb_lookup -i examples/sha256.txt --mode hash --api-key YOUR-KEY --lang en --preview table --live -o out.csv --json-out out.json
```

**2) Signature lookups (inline)**

```bash
python -m mb_lookup --mode signature --values "VenomRAT, AsyncRAT" --limit 800 -o sigs.csv
```

**3) Filename lookups in recent 100**

```bash
python -m mb_lookup --mode name --values "invoice.docx, readme.exe" --recent-selector 100 -o names_recent.csv
```

**4) Filename lookups using full CSV export (offline)**

```bash
python -m mb_lookup --mode name --values "setup.exe" --export-csv /path/to/malwarebazaar_full.csv -o names_full.csv
```

---

## 👀 Live preview modes

* `table` — compact aligned table (great for humans)
* `ndjson` — JSON per line (great for pipes)
* `csv` — CSV header + rows to console

Disable live preview entirely:

```bash
--no-live --preview none
```

---

## 🧾 Output schema

**Both CSV and JSON** contain the exact same fields:

```
first_seen_utc, sha256_hash, md5_hash, sha1_hash, reporter, file_name,
file_type_guess, mime_type, signature, clamav, vtpercent, imphash, ssdeep, tlsh
```

JSON example:

```json
[
  {
    "first_seen_utc": "2025-05-27 13:00:09",
    "sha256_hash": "2b0af18bdd10782cf72a985b2f49564aa90…",
    "md5_hash": "…",
    "sha1_hash": "…",
    "reporter": "…",
    "file_name": "RFQ_PO_783B65_1.zip",
    "file_type_guess": "zip",
    "mime_type": "application/zip",
    "signature": "VenomRAT",
    "clamav": "Win.Trojan.VenomRAT-123",
    "vtpercent": "94",
    "imphash": "",
    "ssdeep": "…",
    "tlsh": "…"
  }
]
```

---

## 🧩 Use as a library (mini-SDK)

```python
from mb_lookup.api import build_session
from mb_lookup.core import get_info_by_hashes
from mb_lookup.config import API_KEY_DEFAULT

api_key = API_KEY_DEFAULT or "YOUR-API-KEY"
session = build_session(retries=3, backoff=1.0, proxy=None)

hashes = [
  "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  # …
]

rows = get_info_by_hashes(
    session=session,
    hashes=hashes,
    api_key=api_key,
    lang="en",
    connect_timeout=10.0,
    read_timeout=45.0,
    verify_tls=True,
    live_ctx=None,            # or use preview.LiveCtx for live printing
    progress_interval=0
)

print("Got", len(rows), "rows")
```

You can also import:

* `get_by_signature`, `get_recent`, `filter_by_name`
* writers: `write_csv`, `write_json`

---

## 🌐 Config & networking

* API key comes from `--api-key` or from `mb_lookup/config.py` (`API_KEY_DEFAULT`).
* Tune networking for your environment (proxies, TLS inspection, etc.).
* The tool prints **rate-limit warnings** (`X-RateLimit-*`) when provided by the server and shows a clear message on **HTTP 429** with **Retry-After**. ⏱️

---

## ⏳ Rate limits

MalwareBazaar enforces daily/hourly quotas.

When you hit the limit you’ll see:

```
Rate limit exceeded (HTTP 429). Retry-After: <seconds>
Rate limit: remaining 0, reset <epoch-seconds>
```

Mitigations:

* Increase `--retries` and `--backoff`
* Reduce RPS / batch inputs (we can add built-in throttling if you need it)
* Prefer CSV export for large offline searches (filename mode)

---

## 🧯 Troubleshooting

* **Looks idle / no output?** Make sure `--live` is enabled (default) and `--preview table`. Add `--progress-interval 10` to see counters.
* **SSL/TLS inspection in corporate networks:** pass `--proxy http://…`. In a pinch, try `--no-verify` (⚠️ not recommended).
* **Windows quoting:** wrap comma/space values in quotes: `--values "h1,h2" "h 3"`.

---

## 🔒 Security notes

* Treat outputs as potentially sensitive threat-intel. 🛡️
---


## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)