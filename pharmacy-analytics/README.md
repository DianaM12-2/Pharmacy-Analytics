# Pharmacy Claims Analytics

A data analytics pipeline that uses **SQL**, **Python**, **pandas**, and **matplotlib** to analyze pharmacy claims data — identifying fraud patterns, spending trends, and patient risk profiles.

---

## Features

- SQLite database with relational schema (patients + claims)
- 6 analytical SQL queries (aggregations, JOINs, GROUP BY, subqueries)
- 4 data visualizations (bar, horizontal bar, line+bar combo, pie)
- Formatted console report
- 6 pytest tests
- GitHub Actions CI

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Core language |
| SQLite | Embedded SQL database |
| pandas | Data manipulation |
| matplotlib | Visualizations |
| pytest | Testing |

---

## Getting Started

```bash
git clone https://github.com/DianaM12-2/pharmacy-analytics.git
cd pharmacy-analytics
pip install -r requirements.txt
python src/analytics.py
```

Charts are saved to `/outputs/`. Console report prints automatically.

### Run tests
```bash
pytest tests/ -v
```

---

## Sample Output

```
=======================================================
  PHARMACY CLAIMS ANALYTICS REPORT
=======================================================

📊 SUMMARY
  Total Claims:   15
  Total Amount:   $3,372.00
  Average Amount: $224.80
  Flagged:        5 (33.3%)
  Approved:       8

🚨 HIGH-VALUE FLAGGED CLAIMS (> $500)
  RX-009  Gabapentin    $780.00  flagged
  RX-003  Atorvastatin  $650.00  flagged
  RX-013  Atorvastatin  $590.00  flagged
```

---

## Charts Generated

- `claims_by_status.png` — Total amount per status
- `top_patients.png` — Top 5 patients by spend
- `monthly_trend.png` — Claims volume and amount over time
- `flagged_distribution.png` — Flagged vs normal pie chart

---

## Author

**Diana Martinez** — [GitHub](https://github.com/DianaM12-2) · [LinkedIn](https://linkedin.com/in/diana-martinez-s)
