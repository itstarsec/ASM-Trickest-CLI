#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trickest ASM CLI (TQL) – phong cách Arsenal

- Dùng API public của Trickest ASM:
  + GET /solutions/v1/public/solution/{solution_id}/dataset  -> list datasets
  + GET /solutions/v1/public/solution/{solution_id}/view     -> query dataset

- Giao diện hỗ trợ:
      *               : q="" (lấy full dataset)
      <query TQL>     : ví dụ: port != 80 AND ip LIKE "10.10.%"
      :limit N        : đặt limit (mặc định 50)
      :offset N       : đặt offset
      :next           : offset += limit
      :prev           : offset -= limit
      :json <query>   : in raw JSON
      :raw            : bật/tắt raw JSON
      :dataset        : đổi dataset
      :fields [kw]    : xem field của dataset, có thể lọc theo keyword
      :help, ?, help  : hiển thị trợ giúp
      :quit, quit, q  : thoát
"""

import json
import sys
import textwrap
import re
from typing import Any, Dict, List, Optional

import requests

# ========= CONFIG TRICKEST (FIXED) =========

API_BASE_URL = "https://api.trickest.io"
SOLUTION_ID = "a7cba1f1-df07-4a5c-876a-953f178996be"
TRICKEST_TOKEN = "0ce7810881195b6ec28c3f2ab1b0bc436b8b2335"

# ========= RICH UI =========

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.panel import Panel
    from rich.traceback import install as rich_traceback_install

    rich_traceback_install()
    console = Console()
    USE_RICH = True
except ImportError:
    console = None
    USE_RICH = False


BANNER = r"""
  ___  
 / _ \  ____  __  __  
| |_| |/ ___||  \/  |
|  _  |\___ \| |\/| |
| | | | ___) | |  | |
|_| |_||____/|_|  |_| 

       Trickest ASM CLI (TQL)
"""

HELP_TEXT = """
Lệnh hỗ trợ:

  *               Lấy full dữ liệu (q="")
  <query TQL>     Ví dụ: ip LIKE "10.10.%", port != 80

  :limit N        Đặt lại limit
  :offset N       Đặt offset
  :next           Sang trang
  :prev           Lùi trang

  :json <query>   In raw JSON
  :raw            Bật/tắt raw JSON sau bảng

  :dataset        Đổi dataset
  :fields [kw]    Xem danh sách field (lọc theo keyword nếu muốn)

  :help, help, ?  Trợ giúp
  :quit, quit, q  Thoát
"""

PREFERRED_FIELDS = [
    "url", "host", "ip", "port", "scheme",
    "status_code", "title", "final_url",
    "webserver", "content_type"
]

# ========= UTILS =========

def strip_html(text: str, max_len: int = 300) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text

def _short(val, width=40):
    s = str(val)
    if len(s) <= width:
        return s
    return s[:width-3] + "..."

def guess_fields(results: List[Dict[str, Any]]) -> List[str]:
    if not results:
        return []
    keys = set()
    for r in results:
        if isinstance(r, dict):
            keys.update(r.keys())

    out = [k for k in PREFERRED_FIELDS if k in keys]
    for k in sorted(keys):
        if k not in out:
            out.append(k)
    return out[:10]

def list_from_response(resp):
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        for k in ("results", "items", "data", "datasets"):
            if k in resp and isinstance(resp[k], list):
                return resp[k]
    return []

# ========= CLIENT =========

class TrickestClient:
    def __init__(self):
        self.base = API_BASE_URL.rstrip("/")
        self.solution = SOLUTION_ID
        self.token = TRICKEST_TOKEN

    def headers(self):
        return {
            "Authorization": f"Token {self.token}",
            "Accept": "application/json"
        }

    def list_datasets(self):
        url = f"{self.base}/solutions/v1/public/solution/{self.solution}/dataset"
        params = {"solution": self.solution}
        r = requests.get(url, headers=self.headers(), params=params, timeout=60)
        if not (200 <= r.status_code < 300):
            raise RuntimeError(f"HTTP {r.status_code} | {strip_html(r.text)}")
        raw = r.json()
        lst = list_from_response(raw)
        return lst if lst else (raw if isinstance(raw, list) else [])

    def query(self, dataset_id, q="", offset=0, limit=50):
        url = f"{self.base}/solutions/v1/public/solution/{self.solution}/view"
        params = {
            "dataset_id": dataset_id,
            "q": q,
            "offset": offset,
            "limit": limit,
        }
        r = requests.get(url, headers=self.headers(), params=params, timeout=60)
        if not (200 <= r.status_code < 300):
            raise RuntimeError(f"HTTP {r.status_code} | {strip_html(r.text)}")
        return r.json()

# ========= TABLE PRINTING =========

def print_results(resp):
    items = list_from_response(resp)
    if not items:
        print("[i] Không có dữ liệu, in raw JSON:")
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return

    cols = guess_fields(items)

    if USE_RICH:
        t = Table(show_lines=False, title="Trickest Results")
        t.add_column("#", style="cyan", no_wrap=True)
        for c in cols:
            t.add_column(c)

        for i, row in enumerate(items, 1):
            t.add_row(str(i), *[_short(row.get(c, "")) for c in cols])

        console.print(t)

    else:
        header = ["#"] + cols
        print(" | ".join(h.ljust(15) for h in header))
        for i, row in enumerate(items, 1):
            print(" | ".join([str(i).ljust(15)] + [_short(row.get(c, ""), 30).ljust(15) for c in cols]))

# ========= DATASET =========

def choose_dataset(client):
    try:
        datasets = client.list_datasets()
    except Exception as e:
        print("[!] Lỗi:", e)
        return None

    if USE_RICH:
        console.print(Panel.fit("Danh sách dataset", border_style="blue", title="Datasets"))

    from rich.table import Table
    t = Table()
    t.add_column("#")
    t.add_column("id")
    t.add_column("name")
    t.add_column("rows")

    for i, d in enumerate(datasets, 1):
        t.add_row(str(i), d.get("id",""), d.get("name",""), str(d.get("rows","")))

    console.print(t)

    while True:
        choice = Prompt.ask("Chọn dataset số mấy (q=thoát)")
        if choice.lower() in ("q", "quit", "exit"):
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(datasets):
            return datasets[int(choice)-1]
        print("[!] Sai số, nhập lại!")

# ========= REPL =========

def repl(client, dataset):
    ds_id = dataset.get("id")
    ds_name = dataset.get("name") or ds_id[:8]

    limit = 50
    offset = 0
    show_raw = False

    if USE_RICH:
        console.print(Panel.fit(f"Dataset: {ds_name}", border_style="green", title="Query Mode"))
        console.print(Panel.fit(HELP_TEXT, border_style="blue", title="Help"))
    else:
        print(HELP_TEXT)

    while True:
        try:
            line = Prompt.ask(f"trickest[{ds_name}]>").strip()
        except:
            print("\nThoát.")
            return

        if not line:
            continue

        # QUIT
        if line in ("q", "quit", "exit", ":quit"):
            print("Thoát.")
            return

        # HELP
        if line in ("help", ":help", "?"):
            print(HELP_TEXT)
            continue

        # LIMIT
        if line.startswith(":limit "):
            try:
                limit = int(line.split()[1])
                print("[i] limit =", limit)
            except:
                print("[!] Limit phải là số.")
            continue

        # OFFSET
        if line.startswith(":offset "):
            try:
                offset = int(line.split()[1])
                print("[i] offset =", offset)
            except:
                print("[!] Offset phải là số.")
            continue

        if line == ":next":
            offset += limit
            print("[i] offset =", offset)
            continue

        if line == ":prev":
            offset = max(0, offset-limit)
            print("[i] offset =", offset)
            continue

        # RAW toggle
        if line == ":raw":
            show_raw = not show_raw
            print("[i] raw =", show_raw)
            continue

        # DATASET
        if line == ":dataset":
            new = choose_dataset(client)
            if new:
                ds_id = new.get("id")
                ds_name = new.get("name", ds_id[:8])
                offset = 0
                print("[i] Đã đổi dataset.")
            continue

        # FIELDS
        if line.startswith(":fields"):
            keyword = line.split(" ",1)[1].strip() if " " in line else ""
            try:
                resp = client.query(ds_id, q="", offset=0, limit=10)
                rows = list_from_response(resp)
                if not rows:
                    print("[i] Không có dữ liệu.")
                    continue
                keys = set()
                for r in rows:
                    if isinstance(r, dict):
                        keys.update(r.keys())
            except Exception as e:
                print("[!] Lỗi:", e)
                continue

            if keyword:
                print(f"[i] Field match '{keyword}':")
                for k in sorted(keys):
                    if keyword.lower() in k.lower():
                        print("-", k)
            else:
                print("[i] Tất cả field:")
                for k in sorted(keys):
                    print("-", k)
            continue

        # JSON
        if line.startswith(":json "):
            q = line.split(" ",1)[1].strip()
            q = "" if q == "*" else q
            try:
                resp = client.query(ds_id, q=q, offset=offset, limit=limit)
                print(json.dumps(resp, indent=2, ensure_ascii=False))
            except Exception as e:
                print("[!] Lỗi:", e)
            continue

        # NORMAL QUERY
        q = "" if line == "*" else line

        if q.startswith(": "):
            q = q[2:]

        try:
            resp = client.query(ds_id, q=q, offset=offset, limit=limit)
        except Exception as e:
            print("[!] Lỗi:", e)
            continue

        print_results(resp)

        if show_raw:
            print("--- RAW ---")
            print(json.dumps(resp, indent=2, ensure_ascii=False))


# ========= MAIN =========

def main():
    client = TrickestClient()
    if USE_RICH:
        console.print(Panel.fit(BANNER, border_style="magenta"))
    else:
        print(BANNER)

    ds = choose_dataset(client)
    if ds is None:
        print("Không chọn dataset, thoát.")
        return

    repl(client, ds)


if __name__ == "__main__":
    main()
