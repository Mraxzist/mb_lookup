# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Mraxzist

import json
from typing import Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import API_URL, I18N, msg, log
from .version import USER_AGENT

def build_session(retries: int, backoff: float, proxy: Optional[str]) -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["POST"]),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    if proxy:
        s.proxies.update({"http": proxy, "https": proxy})
    return s

def maybe_rate_info(resp: requests.Response, lang: str):
    try:
        rem = resp.headers.get("X-RateLimit-Remaining")
        reset = resp.headers.get("X-RateLimit-Reset")
        if rem is not None:
            try:
                if int(rem) <= 2:
                    log(msg(lang, "rate_warn").format(rem=rem, reset=reset))
            except ValueError:
                pass
    except Exception:
        pass

def request_api(
    session: requests.Session,
    data: Dict,
    api_key: str,
    lang: str,
    connect_timeout: float,
    read_timeout: float,
    verify_tls: bool
) -> Dict:
    headers = {"User-Agent": USER_AGENT, "Auth-Key": api_key}
    try:
        resp = session.post(
            API_URL, data=data, headers=headers,
            timeout=(connect_timeout, read_timeout), verify=verify_tls
        )
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "?")
            log(msg(lang, "rate_429").format(v=retry_after))
            resp.raise_for_status()
        resp.raise_for_status()
        maybe_rate_info(resp, lang)
        try:
            payload = resp.json()
        except json.JSONDecodeError:
            raise RuntimeError(msg(lang, "bad_json") + resp.text[:200] + "...")
        qs = str(payload.get("query_status", "")).lower()
        if any(k in qs for k in ["rate", "limit", "quota"]):
            ra = resp.headers.get("Retry-After")
            log(qs + (f" (Retry-After: {ra})" if ra else ""))
        return payload
    except requests.HTTPError as e:
        raise RuntimeError(msg(lang, "http_error") + f"{e} [{getattr(e.response,'status_code',None)}]")
    except requests.RequestException as e:
        raise RuntimeError(msg(lang, "req_error") + str(e))
