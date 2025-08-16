# mb_lookup — массовый поиск по MalwareBazaar (CLI + mini-SDK) 🚀

[English](README.md) | **Русский**

---

## 🎯 Назначение

`mb_lookup` — утилита для **обогащения индикаторов** и **быстрой проверки артефактов** по базе MalwareBazaar в сценариях TI/DFIR/SOC.  
Она помогает быстро понять, **что это за файл**, когда он был **впервые замечен**, к какому **семейству/сигнатуре** относится, и собрать полезные атрибуты (MIME, ClamAV, VT%, imphash, ssdeep, tlsh и т.д.) — **без скачивания и запуска** образцов.

### Где полезна
- 🕵️ **DFIR / реагирование на инциденты**: быстрое обогащение хэшей и файловых артефактов из тикетов/дампов.
- 🛡️ **SOC-триаж**: проверка «известности» вложений/исполняемых файлов по хэшу или семейству.
- 🧪 **Malware-research**: подбор корпусов по сигнатуре/семейству для офлайн-исследований.
- 🔍 **Hunting / Threat Intel**: поворот по `first_seen_utc` и родственным семействам/сигнатурам.

### Что делает
- 🔑 Поиск **по хэшу** (`MD5/SHA1/SHA256`) через `get_info`.
- 🧬 Поиск **по сигнатуре/семейству** через `get_siginfo` (до ~1000 последних результатов).
- 📄 Поиск **по имени файла** — нативного API у MalwareBazaar нет, поэтому инструмент:
  - использует **фильтр “recent”** (последние 100 или последний час), и/или
  - выполняет **офлайн-поиск** по **полным CSV-экспортам** (локальный файл).

### Чего утилита **не** делает
- ⛔ **Не скачивает и не запускает** вредоносные образцы.
- ⛔ **Не обходит** лимиты/политику abuse.ch, **не** является антивирусом или песочницей.
- ⛔ **Не гарантирует** наличие всех полей в каждом ответе (часть атрибутов опциональна на стороне источника).
- ⛔ **Не даёт гарантии**, что если хэш **не найден** в базе, то соответствующий файл **безвреден**.

### Ограничения и нюансы
- 📉 **Лимиты API**: возможны `HTTP 429` и заголовки `X-RateLimit-*`. Инструмент выводит понятные предупреждения и поддерживает бэк-офф/повторы.
- 🔠 **Поиск по имени** носит эвристический характер (recent) или офлайн (CSV-дамп); полное покрытие — через CSV-экспорт.
- 🌐 В корпоративных сетях с прокси/TLS-инспекцией может понадобиться `--proxy` и/или `--no-verify`.

### Дисклеймер ⚠️
Инструмент предназначен **исключительно для легитимных исследований, обучения и обороны** (DFIR/SOC/TI) в рамках закона и локальных политик.  
Вы лично отвечаете за **скачивание/обращение/запуск** образцов и соблюдение всех юридических и лицензионных требований. Автор ответственности не несёт.

---

## ✨ Возможности

- **Типы поиска**
  - `hash` → `get_info` (MD5/SHA1/SHA256 в любом порядке)
  - `signature` → `get_siginfo` (семейство/сигнатура)
  - `name` → фильтр по имени файла в **Recent** или по **локальному CSV-экспорту** (офлайн)
- **Ввод**: из файла (`-i`) и/или напрямую в CLI через `--values "a,b" c d`
- **Вывод**: CSV (`-o out.csv`) и/или JSON (`--json-out out.json`)
- **Потоковый предпросмотр** во время работы: `table` | `ndjson` | `csv` | `none` 👀
- **Устойчивость к ошибкам**: повторы, бэк-офф, таймауты, прокси, переключение проверки TLS
- **Двуязычные логи**: `--lang ru|en`

---

## 🧱 Структура проекта

```

mb\_lookup/
├─ __init__.py
├─ __main__.py         # точка входа модуля: python -m mb\_lookup
├─ api.py              # HTTP-сессия, ретраи, request\_api, сообщения о лимитах
├─ config.py           # константы, i18n, логирование
├─ core.py             # normalize\_item, get\_info\_by\_hashes, get\_by\_signature, …
├─ io_utils.py         # парсинг, запись CSV/JSON, поиск по CSV-экспорту
├─ preview.py          # живой предпросмотр (table/ndjson/csv)
└─ version.py          # версия, user-agent
requirements.txt

````

---

## ⚙️ Установка

```bash
git clone https://github.com/Mraxzist/mb_lookup.git
cd mb_lookup
python -m pip install -r requirements.txt
````

> По желанию можно добавить `pyproject.toml` с консольной командой, чтобы запускать просто `mb_lookup …`.

---

## ❓ Как это запускать?

**Как модуль Python:**

```bash
python -m mb_lookup [опции]
```

Можно также использовать библиотечно — см. раздел «Использование как библиотека».

---

## 🔐 API-ключ

Либо укажите ключ в `mb_lookup/config.py`:

```python
API_KEY_DEFAULT = "YOUR-API-KEY"
```

…либо передавайте в CLI:

```bash
--api-key YOUR-API-KEY
```

> ⚠️ Не коммитьте реальные ключи в публичные репозитории.

---

## 🏃 Быстрый старт

Хэши из файла, живой предпросмотр таблицей, сохранение в CSV и JSON:

```bash
python -m mb_lookup -i sha256.txt \
  --mode hash --api-key YOUR-KEY --lang ru \
  --preview table --live \
  -o out.csv --json-out out.json
```

В консоли будут появляться строки по мере нахождения + счётчики прогресса. ✅

---

## 🛠 CLI: все опции

Показать помощь:

```bash
python -m mb_lookup -h
```

**Базовые опции**

| Опция         | Описание                                                                 |
| ------------- | ------------------------------------------------------------------------ |
| `-m, --mode`  | `hash` \| `signature` \| `name`                                          |
| `-i, --input` | Путь к TXT с запросами (хэши/сигнатуры/имена)                            |
| `--values`    | Запросы прямо в CLI (через пробел или запятую), напр. `--values "h1,h2"` |
| `--api-key`   | API-ключ (или задайте `API_KEY_DEFAULT` в `config.py`)                   |
| `--lang`      | Язык логов: `ru` или `en` (по умолчанию `en`)                            |
| `-o, --out`   | Путь для CSV (используйте `-` для stdout)                                |
| `--json-out`  | Путь для JSON (массив объектов с выбранными полями)                      |

**Опции по режимам**

* `--limit` (signature): максимум результатов на сигнатуру (≤ 1000)
* `--recent-selector` (name): `time` (последний час) или `100` (последние 100)
* `--export-csv` (name): путь к полному CSV-экспорту MalwareBazaar для офлайн-поиска по имени

**Сеть/устойчивость**

* `--connect-timeout` (по умолчанию 10s), `--read-timeout` (по умолчанию 45s)
* `--retries` (по умолчанию 3), `--backoff` (по умолчанию 1.0)
* `--proxy http://127.0.0.1:8080`
* `--verify` / `--no-verify` (TLS)

**Предпросмотр/прогресс**

* `--live` / `--no-live` — потоковый вывод по мере получения (по умолчанию `--live`)
* `--preview table|ndjson|csv|none` (по умолчанию `table`)
* `--progress-interval 25` — печать **Processed X/Y** каждые N элементов

---

## 📚 Примеры

**1) Поиск по хэшам (файл + live)**

```bash
python -m mb_lookup -i examples/sha256.txt \
  --mode hash --api-key YOUR-KEY --lang ru \
  --preview table --live \
  -o out.csv --json-out out.json
```

**2) Поиск по сигнатурам (из CLI)**

```bash
python -m mb_lookup --mode signature \
  --values "VenomRAT, AsyncRAT" --limit 800 \
  -o sigs.csv
```

**3) Поиск по имени среди последних 100**

```bash
python -m mb_lookup --mode name \
  --values "invoice.docx, readme.exe" \
  --recent-selector 100 -o names_recent.csv
```

**4) Поиск по имени в полном CSV-дампе (офлайн)**

```bash
python -m mb_lookup --mode name \
  --values "setup.exe" \
  --export-csv /path/to/malwarebazaar_full.csv \
  -o names_full.csv
```

---

## 👀 Режимы предпросмотра (live)

* `table` — компактная выровненная таблица (удобно глазами)
* `ndjson` — JSON построчно (удобно для пайпов)
* `csv` — заголовок и строки CSV в консоль

Полностью отключить предпросмотр:

```bash
--no-live --preview none
```

---

## 🧾 Схема вывода

И **CSV**, и **JSON** содержат одинаковые поля:

```
first_seen_utc, sha256_hash, md5_hash, sha1_hash, reporter, file_name,
file_type_guess, mime_type, signature, clamav, vtpercent, imphash, ssdeep, tlsh
```

Пример JSON:

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

## 🧩 Использование как библиотеки (mini-SDK)

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
    lang="ru",
    connect_timeout=10.0,
    read_timeout=45.0,
    verify_tls=True,
    live_ctx=None,            # можно передать preview.LiveCtx для живого вывода
    progress_interval=0
)

print("Получено записей:", len(rows))
```

Также доступны:

* `get_by_signature`, `get_recent`, `filter_by_name`
* writers: `write_csv`, `write_json`

---

## 🌐 Конфигурация и сеть

* Ключ берётся из `--api-key` или из `mb_lookup/config.py` (`API_KEY_DEFAULT`).
* Настройки сети под вашу среду: таймауты/ретраи/бэк-офф, `--proxy`, `--verify/--no-verify`.
* При достижении лимитов выводятся предупреждения `X-RateLimit-*` и понятное сообщение на **HTTP 429** с **Retry-After**. ⏱️

---

## ⏳ Лимиты

У MalwareBazaar есть почасовые/суточные лимиты.

При достижении лимита вы увидите, например:

```
Rate limit exceeded (HTTP 429). Retry-After: <seconds>
Rate limit: remaining 0, reset <epoch-seconds>
```

Как смягчить:

* Увеличить `--retries` и `--backoff`
* Снизить RPS / батчить входные данные (можно добавить встроенный троттлинг при необходимости)
* Для массового офлайн-поиска по именам использовать CSV-экспорт

---

## 🧯 Трюки и отладка

* **Тишина в консоли?** Убедитесь, что включён live-режим (по умолчанию включён) и `--preview table`. Добавьте `--progress-interval 10`.
* **TLS-инспекция/прокси в организации:** передайте `--proxy http://…`. В крайнем случае `--no-verify` (⚠️ рискованно).
* **Кавычки в Windows:** значения с пробелами/запятыми оборачивайте в кавычки: `--values "h1,h2" "h 3"`.

---

## 🔒 Безопасность

* Относитесь к выводимым данным как к чувствительному TI. 🛡️

---

## License

Этот проект лицензирован по лицензии mit — смотрите [LICENSE](./LICENSE) файл с подробностями.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)