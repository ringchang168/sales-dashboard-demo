"""Interactive dashboard for the public, synthetic sales dataset."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from sales_dashboard import (
    filter_sales,
    load_sales,
    metrics,
    monthly_sales,
    parse_filter_date,
    sales_by,
)


DATA_PATH = Path(__file__).parent / "data" / "sales.csv"

st.set_page_config(page_title="業績互動分析儀表板", page_icon="📊", layout="wide")


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_sales(DATA_PATH)


st.title("📊 業績互動分析儀表板")
st.caption("第三階段作品 3-1｜沿用 2-2 業績資料報表自動化的公開模擬資料")

try:
    sales = get_data()
except (OSError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"無法讀取銷售資料：{exc}")
    st.stop()

if sales.empty:
    st.warning("銷售資料目前沒有紀錄。")
    st.stop()

minimum = sales["銷售日期"].min().date()
maximum = sales["銷售日期"].max().date()
all_units = sorted(sales["業務單位"].unique().tolist())
all_products = sorted(sales["銷售產品"].unique().tolist())

with st.sidebar:
    title_col, mode_col = st.columns([1.5, 3], gap="small")
    with title_col:
        st.markdown("**篩選條件**")
    with mode_col:
        date_mode = st.radio(
            "日期輸入方式", ("日曆", "手動"), horizontal=True, label_visibility="collapsed"
        )
    if date_mode == "日曆":
        chosen_dates = st.date_input(
            "銷售日期區間", value=(minimum, maximum), min_value=minimum, max_value=maximum
        )
        st.caption("請選有效日期；若手動鍵入無效日期，右側會維持上次結果。想看錯誤原因，請選「手動」。")
        date_error = None
    else:
        start_text = st.text_input("開始日期（YYYY/MM/DD）", value=f"{minimum:%Y/%m/%d}")
        end_text = st.text_input("結束日期（YYYY/MM/DD）", value=f"{maximum:%Y/%m/%d}")
        st.caption("輸入後按 Enter 或點到欄位外，日期檢查與圖表才會更新。")
        try:
            start_date = parse_filter_date(start_text, "開始日期", minimum, maximum)
            end_date = parse_filter_date(end_text, "結束日期", minimum, maximum)
            if start_date > end_date:
                raise ValueError("開始日期不能晚於結束日期。")
        except ValueError as exc:
            chosen_dates = ()
            date_error = str(exc)
            st.error(date_error)
        else:
            chosen_dates = (start_date, end_date)
            date_error = None
    chosen_units = st.multiselect("業務單位", all_units, default=all_units)
    chosen_products = st.multiselect("銷售產品", all_products, default=all_products)
    st.divider()
    st.caption("所有資料均為模擬資料；金額不代表真實營收。")

if date_error:
    st.error(f"日期輸入有誤：{date_error}")
    st.stop()

if len(chosen_dates) != 2:
    st.info("請選取開始與結束日期。")
    st.stop()

filtered = filter_sales(sales, chosen_dates[0], chosen_dates[1], chosen_units, chosen_products)
if filtered.empty:
    st.info("目前篩選條件沒有資料；請調整日期、業務單位或產品。")
    st.stop()

summary = metrics(filtered)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("銷售總額", f"NT$ {summary['total_sales']:,.0f}")
kpi2.metric("交易筆數", f"{summary['transaction_count']:,}")
kpi3.metric("銷售數量", f"{summary['units_sold']:,}")
kpi4.metric("平均每筆金額", f"NT$ {summary['average_transaction']:,.0f}")
st.caption("交易筆數＝資料列數；平均每筆金額＝銷售總額 ÷ 交易筆數。")

trend = monthly_sales(filtered)
st.subheader("月度銷售趨勢")
trend_chart = px.line(
    trend,
    x="月份",
    y="銷售金額",
    markers=True,
    labels={"月份": "月份", "銷售金額": "銷售金額（元）"},
)
trend_chart.update_traces(line_color="#2563eb", hovertemplate="%{x|%Y-%m}<br>NT$ %{y:,.0f}<extra></extra>")
trend_chart.update_layout(hovermode="x unified", margin=dict(l=8, r=8, t=12, b=8))
st.plotly_chart(trend_chart, width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("業務單位排名")
    unit_totals = sales_by(filtered, "業務單位")
    unit_chart = px.bar(
        unit_totals,
        x="銷售金額",
        y="業務單位",
        orientation="h",
        category_orders={"業務單位": unit_totals["業務單位"].tolist()[::-1]},
        labels={"銷售金額": "銷售金額（元）"},
    )
    unit_chart.update_traces(marker_color="#0f766e", hovertemplate="%{y}<br>NT$ %{x:,.0f}<extra></extra>")
    unit_chart.update_layout(margin=dict(l=8, r=8, t=12, b=8))
    st.plotly_chart(unit_chart, width="stretch")

with right:
    st.subheader("產品銷售排名")
    product_totals = sales_by(filtered, "銷售產品")
    product_chart = px.bar(
        product_totals,
        x="銷售金額",
        y="銷售產品",
        orientation="h",
        category_orders={"銷售產品": product_totals["銷售產品"].tolist()[::-1]},
        labels={"銷售金額": "銷售金額（元）"},
    )
    product_chart.update_traces(marker_color="#d97706", hovertemplate="%{y}<br>NT$ %{x:,.0f}<extra></extra>")
    product_chart.update_layout(margin=dict(l=8, r=8, t=12, b=8))
    st.plotly_chart(product_chart, width="stretch")

st.subheader("篩選後銷售明細")
display = filtered.sort_values("銷售日期", ascending=False).copy()
display["銷售日期"] = display["銷售日期"].dt.strftime("%Y-%m-%d")
st.dataframe(display, hide_index=True, width="stretch")
st.download_button(
    "下載篩選後明細 CSV",
    data=("\ufeff" + display.to_csv(index=False)).encode("utf-8"),
    file_name="filtered_sales.csv",
    mime="text/csv",
)
