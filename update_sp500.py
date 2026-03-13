#!/usr/bin/env python3
"""
从 Wikipedia 更新 sp500.csv，检测成分股变化。
有变化时：覆写 sp500.csv，将摘要写入 CHANGES.txt。
"""

import io
import os

import pandas as pd
import requests

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
FILENAME = "sp500.csv"
CHANGES_FILE = "CHANGES.txt"


def fetch_from_wikipedia() -> pd.DataFrame:
    resp = requests.get(WIKI_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    df = pd.read_html(io.StringIO(resp.text), match="Symbol")[0]
    return df


def main() -> None:
    print("正在从 Wikipedia 获取 S&P 500 成分股...")
    new_df = fetch_from_wikipedia()
    new_symbols = set(new_df["Symbol"].astype(str))

    if os.path.isfile(FILENAME):
        old_df = pd.read_csv(FILENAME)
        old_symbols = set(old_df["Symbol"].astype(str))

        added = sorted(new_symbols - old_symbols)
        removed = sorted(old_symbols - new_symbols)

        if not added and not removed:
            print("无变化，sp500.csv 已是最新。")
            return

        new_df.to_csv(FILENAME, index=False, encoding="utf-8")

        parts = []
        if added:
            tickers = "  ".join(f"<code>{t}</code>" for t in added)
            parts.append(f"🟢 <b>新增 {len(added)} 支</b>\n{tickers}")
        if removed:
            tickers = "  ".join(f"<code>{t}</code>" for t in removed)
            parts.append(f"🔴 <b>移出 {len(removed)} 支</b>\n{tickers}")
        parts.append(f"共 {len(new_df)} 支成分股")

        summary = "\n\n".join(parts)
        print(summary)

        with open(CHANGES_FILE, "w", encoding="utf-8") as f:
            f.write(summary)
    else:
        new_df.to_csv(FILENAME, index=False, encoding="utf-8")
        print(f"首次创建 sp500.csv（共 {len(new_df)} 支）")


if __name__ == "__main__":
    main()
