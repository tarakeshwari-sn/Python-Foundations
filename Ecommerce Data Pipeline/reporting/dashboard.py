import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
import os

# Database Connection
DSN = os.getenv("POSTGRES_DSN", "host=localhost port=5432 dbname=ecommerce_olap user=airflow password=airflow")

def fetch_data(query):
    with psycopg2.connect(DSN) as conn:
        return pd.read_sql(query, conn)

def generate_dashboard():
    # 1. Fetch KPIs
    kpi_query = """
    SELECT 
        SUM(total_amount) as total_revenue,
        COUNT(sales_id) as total_orders,
        AVG(total_amount) as avg_order_value
    FROM fact_sales;
    """
    kpis = fetch_data(kpi_query)
    
    # 2. Daily Revenue Trend (Line Chart)
    trend_query = """
    SELECT d.full_date, SUM(f.total_amount) as daily_revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY d.full_date
    ORDER BY d.full_date;
    """
    trend_df = fetch_data(trend_query)
    trend_df['full_date'] = pd.to_datetime(trend_df['full_date'])

    # 3. Revenue by Category (Bar Chart)
    category_query = """
    SELECT p.category, SUM(f.total_amount) as category_revenue
    FROM fact_sales f
    JOIN dim_product p ON f.product_sk = p.product_sk
    GROUP BY p.category
    ORDER BY category_revenue DESC;
    """
    category_df = fetch_data(category_query)

    # Create Dashboard Layout
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(3, 6, height_ratios=[1, 4, 4])
    fig.patch.set_facecolor('#f4f4f4')
    plt.subplots_adjust(hspace=0.4, wspace=0.3)

    # Title
    fig.suptitle('E-Commerce Business Intelligence Dashboard', fontsize=24, fontweight='bold', color='#2c3e50', y=0.95)

    # KPI 1: Total Revenue
    ax_kpi1 = fig.add_subplot(gs[0, 0:2])
    ax_kpi1.axis('off')
    ax_kpi1.text(0.5, 0.6, 'TOTAL REVENUE', ha='center', va='center', fontsize=12, color='#7f8c8d')
    ax_kpi1.text(0.5, 0.3, f"${kpis['total_revenue'][0]:,.2f}", ha='center', va='center', fontsize=24, fontweight='bold', color='#27ae60')

    # KPI 2: Total Orders
    ax_kpi2 = fig.add_subplot(gs[0, 2:4])
    ax_kpi2.axis('off')
    ax_kpi2.text(0.5, 0.6, 'TOTAL ORDERS', ha='center', va='center', fontsize=12, color='#7f8c8d')
    ax_kpi2.text(0.5, 0.3, f"{kpis['total_orders'][0]:,}", ha='center', va='center', fontsize=24, fontweight='bold', color='#2980b9')

    # KPI 3: Avg Order Value
    ax_kpi3 = fig.add_subplot(gs[0, 4:6])
    ax_kpi3.axis('off')
    ax_kpi3.text(0.5, 0.6, 'AVG ORDER VALUE', ha='center', va='center', fontsize=12, color='#7f8c8d')
    ax_kpi3.text(0.5, 0.3, f"${kpis['avg_order_value'][0]:,.2f}", ha='center', va='center', fontsize=24, fontweight='bold', color='#8e44ad')

    # Plot 1: Daily Revenue Trend (Line Chart)
    ax1 = fig.add_subplot(gs[1, :])
    sns.lineplot(data=trend_df, x='full_date', y='daily_revenue', ax=ax1, color='#e67e22', linewidth=2.5, marker='o')
    ax1.set_title('Daily Revenue Trend', fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Revenue ($)', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)

    # Plot 2: Revenue by Product Category (Bar Chart)
    ax2 = fig.add_subplot(gs[2, 0:3])
    sns.barplot(data=category_df, x='category_revenue', y='category', ax=ax2, hue='category', palette='viridis', legend=False)
    ax2.set_title('Revenue by Category', fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('Revenue ($)', fontsize=12)
    ax2.set_ylabel('Category', fontsize=12)

    # Plot 3: Order Volume Distribution (Simulated/Pie)
    ax3 = fig.add_subplot(gs[2, 3:6])
    colors = sns.color_palette('pastel')[0:len(category_df)]
    ax3.pie(category_df['category_revenue'], labels=category_df['category'], autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops={'edgecolor': 'white'})
    ax3.set_title('Revenue Share by Category', fontsize=16, fontweight='bold', pad=20)

    # Save Dashboard
    output_path = os.path.join(os.path.dirname(__file__), 'dashboard.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Dashboard saved to: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
