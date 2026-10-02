import unittest
from datetime import date
from pathlib import Path

from sales_dashboard import filter_sales, load_sales, metrics, monthly_sales, parse_filter_date, sales_by


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sales.csv"


class SalesDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sales = load_sales(DATA_PATH)
        cls.units = cls.sales["業務單位"].unique().tolist()
        cls.products = cls.sales["銷售產品"].unique().tolist()

    def test_public_source_baseline(self):
        self.assertEqual(len(self.sales), 896)
        self.assertEqual(metrics(self.sales)["total_sales"], 81_374_300)
        self.assertEqual(self.sales["銷售日期"].min().date(), date(2022, 1, 5))
        self.assertEqual(self.sales["銷售日期"].max().date(), date(2025, 10, 27))

    def test_filters_are_inclusive_and_change_metrics(self):
        result = filter_sales(self.sales, date(2022, 1, 5), date(2022, 1, 31), self.units[:1], self.products)
        self.assertGreater(len(result), 0)
        self.assertTrue(result["銷售日期"].dt.date.between(date(2022, 1, 5), date(2022, 1, 31)).all())
        self.assertEqual(set(result["業務單位"]), {self.units[0]})
        self.assertLess(metrics(result)["total_sales"], metrics(self.sales)["total_sales"])

    def test_empty_filter_has_zero_average(self):
        result = filter_sales(self.sales, date(2022, 1, 5), date(2025, 10, 27), [], self.products)
        self.assertTrue(result.empty)
        self.assertEqual(metrics(result)["average_transaction"], 0)

    def test_groupings_reconcile_with_total(self):
        total = metrics(self.sales)["total_sales"]
        self.assertEqual(int(monthly_sales(self.sales)["銷售金額"].sum()), total)
        self.assertEqual(int(sales_by(self.sales, "業務單位")["銷售金額"].sum()), total)
        self.assertEqual(int(sales_by(self.sales, "銷售產品")["銷售金額"].sum()), total)

    def test_manual_date_validation(self):
        minimum, maximum = date(2022, 1, 5), date(2025, 10, 27)
        self.assertEqual(parse_filter_date("2025/08/31", "結束日期", minimum, maximum), date(2025, 8, 31))
        for invalid in ("2025/08/88", "2025/13/01", "2025-08-31", "2026/01/01"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_filter_date(invalid, "結束日期", minimum, maximum)


if __name__ == "__main__":
    unittest.main()
