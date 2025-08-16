# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Mraxzist

import re, sys
from typing import Dict

API_URL = "https://mb-api.abuse.ch/api/v1/"

# Впиши ключ по умолчанию, если не хочешь передавать --api-key
# Enter the default key if you don't want to transmit the --api-key
API_KEY_DEFAULT = "PUT-YOUR-API-KEY-HERE"

CSV_FIELDS = [
    "first_seen_utc","sha256_hash","md5_hash","sha1_hash","reporter",
    "file_name","file_type_guess","mime_type","signature","clamav",
    "vtpercent","imphash","ssdeep","tlsh",
]

HEX_RE = re.compile(r"\b([a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64})\b")

I18N = {
    "en": {
        "need_api": "API key is required. Pass --api-key or set API_KEY_DEFAULT in the script.",
        "no_hashes": "No MD5/SHA1/SHA256 values were found.",
        "reading_file": "Reading file: ",
        "mode_hash": "Mode: hash",
        "mode_sig": "Mode: signature",
        "mode_name": "Mode: name",
        "bad_json": "Bad JSON from API: ",
        "http_error": "HTTP error: ",
        "req_error": "Request error: ",
        "writing_csv": "Writing CSV to: ",
        "writing_json": "Writing JSON to: ",
        "interrupted": "Interrupted by user (Ctrl+C). Writing partial results...",
        "no_results": "No results.",
        "found_n": "Found rows: {n}",
        "rate_429": "Rate limit exceeded (HTTP 429). Retry-After: {v}",
        "rate_warn": "Rate limit: remaining {rem}, reset {reset}",
        "streaming": "Streaming results...",
        "processed": "Processed {i}/{n}",
        "preview_header": "Preview (first {n} rows):",
        "cols": {
            "first_seen_utc": "first_seen_utc",
            "sha256_hash": "sha256",
            "file_name": "file_name",
            "signature": "signature",
            "vtpercent": "vt%",
        },
    },
    "ru": {
        "need_api": "Требуется ключ API. Передай --api-key или пропиши API_KEY_DEFAULT в скрипте.",
        "no_hashes": "Не найдено значений MD5/SHA1/SHA256.",
        "reading_file": "Чтение из файла: ",
        "mode_hash": "Режим: hash",
        "mode_sig": "Режим: signature",
        "mode_name": "Режим: name",
        "bad_json": "Некорректный JSON от API: ",
        "http_error": "HTTP-ошибка: ",
        "req_error": "Сетевая ошибка: ",
        "writing_csv": "Запись CSV в: ",
        "writing_json": "Запись JSON в: ",
        "interrupted": "Прервано пользователем (Ctrl+C). Записываю накопленные результаты...",
        "no_results": "Результатов нет.",
        "found_n": "Найдено строк: {n}",
        "rate_429": "Превышен лимит запросов (HTTP 429). Повторить через: {v}",
        "rate_warn": "Лимит запросов: осталось {rem}, сброс {reset}",
        "streaming": "Потоковый вывод результатов...",
        "processed": "Обработано {i}/{n}",
        "preview_header": "Предпросмотр (первые {n} строк):",
        "cols": {
            "first_seen_utc": "first_seen_utc",
            "sha256_hash": "sha256",
            "file_name": "file_name",
            "signature": "signature",
            "vtpercent": "vt%",
        },
    },
}

def msg(lang: str, key: str) -> str:
    return I18N.get(lang, I18N["en"]).get(key, key)

def log(s: str) -> None:
    sys.stderr.write(s + "\n")
