"""
Pharmacy Claims Analytics
Demonstrates: SQL queries with Python, data analysis with pandas,
visualizations with matplotlib, and OOP data pipeline design.

Author: Diana Martinez
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


# ──────────────────────────────────────────────
# Data Layer — SQL + SQLite
# ──────────────────────────────────────────────

def create_database(conn: sqlite3.Connection) -> None:
    """Create schema and seed data."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id          INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL,
            age         INTEGER,
            state       TEXT
        );

        CREATE TABLE IF NOT EXISTS claims (
            id          INTEGER PRIMARY KEY,
            claim_id    TEXT    UNIQUE NOT NULL,
            patient_id  INTEGER REFERENCES patients(id),
            medication  TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            status      TEXT    DEFAULT 'pending',
            flagged     INTEGER DEFAULT 0,
            created_date TEXT
        );

        INSERT OR IGNORE INTO patients VALUES
          (1, 'Maria Garcia',   67, 'VA'),
          (2, 'James Wilson',   54, 'MD'),
          (3, 'Sarah Johnson',  72, 'DC'),
          (4, 'Robert Chen',    45, 'VA'),
          (5, 'Linda Martinez', 61, 'MD'),
          (6, 'David Kim',      38, 'VA'),
          (7, 'Jennifer Lee',   58, 'DC'),
          (8, 'Michael Brown',  49, 'MD');

        INSERT OR IGNORE INTO claims VALUES
          (1,  'RX-001', 1, 'Lisinopril',   45.00,  'approved', 0, '2026-01-15'),
          (2,  'RX-002', 2, 'Metformin',    120.00, 'approved', 0, '2026-01-20'),
          (3,  'RX-003', 3, 'Atorvastatin', 650.00, 'flagged',  1, '2026-01-22'),
          (4,  'RX-004', 1, 'Omeprazole',   89.00,  'approved', 0, '2026-02-01'),
          (5,  'RX-005', 1, 'Amlodipine',   75.00,  'flagged',  1, '2026-02-10'),
          (6,  'RX-006', 4, 'Metoprolol',   210.00, 'approved', 0, '2026-02-14'),
          (7,  'RX-007', 5, 'Levothyroxine',55.00,  'pending',  0, '2026-02-20'),
          (8,  'RX-008', 6, 'Sertraline',   95.00,  'approved', 0, '2026-03-01'),
          (9,  'RX-009', 7, 'Gabapentin',   780.00, 'flagged',  1, '2026-03-05'),
          (10, 'RX-010', 8, 'Hydrocodone',  320.00, 'flagged',  1, '2026-03-10'),
          (11, 'RX-011', 2, 'Lisinopril',   48.00,  'approved', 0, '2026-03-15'),
          (12, 'RX-012', 3, 'Metformin',    125.00, 'approved', 0, '2026-03-20'),
          (13, 'RX-013', 4, 'Atorvastatin', 590.00, 'flagged',  1, '2026-04-01'),
          (14, 'RX-014', 5, 'Omeprazole',   92.00,  'approved', 0, '2026-04-05'),
          (15, 'RX-015', 6, 'Amlodipine',   78.00,  'approved', 0, '2026-04-10');
    """)
    conn.commit()


# ──────────────────────────────────────────────
# Analytics Queries
# ──────────────────────────────────────────────

QUERIES = {
    "summary": """
        SELECT
            COUNT(*)                                    AS total_claims,
            ROUND(SUM(amount), 2)                       AS total_amount,
            ROUND(AVG(amount), 2)                       AS avg_amount,
            SUM(CASE WHEN flagged = 1 THEN 1 ELSE 0 END) AS flagged_count,
            SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) AS approved_count
        FROM claims
    """,

    "by_status": """
        SELECT status, COUNT(*) AS count, ROUND(SUM(amount), 2) AS total
        FROM claims GROUP BY status ORDER BY total DESC
    """,

    "top_patients": """
        SELECT p.name, COUNT(c.id) AS claim_count, ROUND(SUM(c.amount), 2) AS total_spent
        FROM patients p
        JOIN claims c ON p.id = c.patient_id
        GROUP BY p.id
        ORDER BY total_spent DESC
        LIMIT 5
    """,

    "flagged_by_state": """
        SELECT p.state, COUNT(*) AS flagged_claims, ROUND(SUM(c.amount), 2) AS total_flagged
        FROM claims c
        JOIN patients p ON c.patient_id = p.id
        WHERE c.flagged = 1
        GROUP BY p.state
        ORDER BY flagged_claims DESC
    """,

    "monthly_trend": """
        SELECT
            SUBSTR(created_date, 1, 7) AS month,
            COUNT(*) AS claims,
            ROUND(SUM(amount), 2) AS total
        FROM claims
        GROUP BY month
        ORDER BY month
    """,

    "high_value": """
        SELECT c.claim_id, p.name, c.medication, c.amount, c.status
        FROM claims c
        JOIN patients p ON c.patient_id = p.id
        WHERE c.amount > 500
        ORDER BY c.amount DESC
    """
}


# ──────────────────────────────────────────────
# Visualization
# ──────────────────────────────────────────────

def plot_all(conn: sqlite3.Connection, output_dir: Path) -> None:
    """Generate all charts and save to output directory."""
    output_dir.mkdir(exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    # 1. Claims by status (bar chart)
    df_status = pd.read_sql_query(QUERIES["by_status"], conn)
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {"approved": "#2ecc71", "flagged": "#e74c3c", "pending": "#f39c12"}
    bar_colors = [colors.get(s, "#95a5a6") for s in df_status["status"]]
    ax.bar(df_status["status"], df_status["total"], color=bar_colors, edgecolor="white")
    ax.set_title("Total Claim Amount by Status", fontsize=14, fontweight="bold")
    ax.set_xlabel("Status")
    ax.set_ylabel("Total Amount ($)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    for i, (_, row) in enumerate(df_status.iterrows()):
        ax.text(i, row["total"] + 20, f"${row['total']:,.0f}", ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(output_dir / "claims_by_status.png", dpi=150)
    plt.close()

    # 2. Top patients (horizontal bar)
    df_patients = pd.read_sql_query(QUERIES["top_patients"], conn)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(df_patients["name"], df_patients["total_spent"], color="#3498db", edgecolor="white")
    ax.set_title("Top 5 Patients by Total Claim Amount", fontsize=14, fontweight="bold")
    ax.set_xlabel("Total Amount ($)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    plt.savefig(output_dir / "top_patients.png", dpi=150)
    plt.close()

    # 3. Monthly trend (line chart)
    df_trend = pd.read_sql_query(QUERIES["monthly_trend"], conn)
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    ax1.plot(df_trend["month"], df_trend["total"], color="#e74c3c", marker="o", linewidth=2, label="Total Amount")
    ax2.bar(df_trend["month"], df_trend["claims"], alpha=0.3, color="#3498db", label="# Claims")
    ax1.set_title("Monthly Claims Trend", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Total Amount ($)", color="#e74c3c")
    ax2.set_ylabel("Number of Claims", color="#3498db")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    plt.savefig(output_dir / "monthly_trend.png", dpi=150)
    plt.close()

    # 4. Flagged vs normal pie chart
    df_sum = pd.read_sql_query(QUERIES["summary"], conn)
    total = int(df_sum["total_claims"].iloc[0])
    flagged = int(df_sum["flagged_count"].iloc[0])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie([flagged, total - flagged],
           labels=["Flagged", "Normal"],
           colors=["#e74c3c", "#2ecc71"],
           autopct="%1.1f%%", startangle=90,
           wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax.set_title("Flagged vs Normal Claims", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_dir / "flagged_distribution.png", dpi=150)
    plt.close()

    print(f"✅ Charts saved to {output_dir}/")


# ──────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────

def print_report(conn: sqlite3.Connection) -> None:
    """Print a formatted analytics report to the console."""
    print("\n" + "=" * 55)
    print("  PHARMACY CLAIMS ANALYTICS REPORT")
    print("=" * 55)

    summary = pd.read_sql_query(QUERIES["summary"], conn).iloc[0]
    print(f"\n📊 SUMMARY")
    print(f"  Total Claims:   {int(summary['total_claims'])}")
    print(f"  Total Amount:   ${summary['total_amount']:,.2f}")
    print(f"  Average Amount: ${summary['avg_amount']:,.2f}")
    print(f"  Flagged:        {int(summary['flagged_count'])} ({summary['flagged_count']/summary['total_claims']*100:.1f}%)")
    print(f"  Approved:       {int(summary['approved_count'])}")

    print(f"\n🚨 HIGH-VALUE FLAGGED CLAIMS (> $500)")
    df_hv = pd.read_sql_query(QUERIES["high_value"], conn)
    print(df_hv.to_string(index=False))

    print(f"\n🗺️  FLAGGED CLAIMS BY STATE")
    df_state = pd.read_sql_query(QUERIES["flagged_by_state"], conn)
    print(df_state.to_string(index=False))

    print(f"\n👤 TOP 5 PATIENTS BY TOTAL SPEND")
    df_patients = pd.read_sql_query(QUERIES["top_patients"], conn)
    print(df_patients.to_string(index=False))
    print("\n" + "=" * 55)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    create_database(conn)
    print_report(conn)
    plot_all(conn, Path("outputs"))
    conn.close()
