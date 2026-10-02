"""Data preparation and metrics for the synthetic sales dashboard."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import re

import pandas as pd


REQUIRED_COLUMNS = (
    "銷售日期",
    "業務單位",
    "業務員",
    "性別",
    "銷售產品",
    "銷售數量",
    "銷售金額",
)


def parse_filter_date(text: str, label: str, minimum: date, maximum: date) -> date:
    """Validate a manually entered YYYY/MM/DD date before filtering."""
    if not re.fullmatch(r"\d{4}/\d{2}/\d{2}", text.strip()):
        raise ValueError(f"{label}格式不正確，請輸入 YYYY/MM/DD，例如 2025/08/31。")
    try:
        parsed = date.fromisoformat(text.strip().replace("/", "-"))
    except ValueError as exc:
        raise ValueError(f"{label}不是有效日期，請檢查月份和日期（例如 8 月沒有 88 日）。") from exc
    if not minimum <= parsed <= maximum:
        raise ValueError(
            f"{label}須介於 {minimum:%Y/%m/%d} 與 {maximum:%Y/%m/%d} 之間。"
        )
    return parsed


def load_sales(path: str | Path) -> pd.DataFrame:
    """Load and validate the unchanged UTF-8 CSV from the previous project."""
    data = pd.read_csv(path, encoding="utf-8-sig")
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"資料缺少欄位：{', '.join(missing)}")

    data = data.loc[:, REQUIRED_COLUMNS].copy()
    data["銷售日期"] = pd.to_datetime(data["銷售日期"], errors="raise")
    for column in ("銷售數量", "銷售金額"):
        data[column] = pd.to_numeric(data[column], errors="raise")
        if data[column].isna().any() or (data[column] < 0).any():
            raise ValueError(f"{column}不能有空值或負數")
    if data[list(REQUIRED_COLUMNS[:5])].isna().any().any():
        raise ValueError("資料文字欄位不能有空值")
    return data.sort_values("銷售日期").reset_index(drop=True)


def filter_sales(
    data: pd.DataFrame,
    start_date,
    end_date,
    units: list[str],
    products: list[str],
) -> pd.DataFrame:
    """Filter inclusively by calendar date, unit and product."""
    if start_date > end_date or not units or not products:
        return data.iloc[0:0].copy()
    dates = data["銷售日期"].dt.date
    mask = (
        dates.between(start_date, end_date)
        & data["業務單位"].isin(units)
        & data["銷售產品"].isin(products)
    )
    return data.loc[mask].copy()


def metrics(data: pd.DataFrame) -> dict[str, float | int]:
    count = len(data)
    total = int(data["銷售金額"].sum())
    return {
        "total_sales": total,
        "transaction_count": count,
        "units_sold": int(data["銷售數量"].sum()),
        "average_transaction": total / count if count else 0,
    }


def monthly_sales(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(columns=["月份", "銷售金額"])
    monthly = (
        data.assign(月份=data["銷售日期"].dt.to_period("M"))
        .groupby("月份", as_index=False)["銷售金額"]
        .sum()
    )
    monthly["月份"] = monthly["月份"].dt.to_timestamp()
    return monthly


def sales_by(data: pd.DataFrame, column: str) -> pd.DataFrame:
    if column not in ("業務單位", "銷售產品"):
        raise ValueError("只能依業務單位或銷售產品彙總")
    return (
        data.groupby(column, as_index=False)["銷售金額"]
        .sum()
        .sort_values("銷售金額", ascending=False, kind="stable")
        .reset_index(drop=True)
    )
