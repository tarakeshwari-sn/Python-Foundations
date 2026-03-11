import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import RadioButtons, Button
from datetime import datetime
import matplotlib.gridspec as gridspec

# Configuration
POSTGRES_DSN = "host=127.0.0.1 port=5432 dbname=ecommerce_olap user=airflow password=airflow"

def query(sql):
    try:
        conn = psycopg2.connect(POSTGRES_DSN)
        df = pd.read_sql(sql,conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Database Error: {e}")
        return pd.DataFrame()

class EcommerceDashboard:
    def __init__(self):
        self.year = 2024
        self.month = 0  # 0 means All Months
        self.years = [2024, 2023]
        self.months = ["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        # Setup Figure
        plt.style.use("dark_background")
        self.fig = plt.figure(figsize=(18, 10))
        self.fig.canvas.manager.set_window_title('E-commerce Data Pipeline - Analytics Dashboard')
        self.gs = gridspec.GridSpec(4, 4, figure=self.fig, height_ratios=[0.1, 0.45, 0.45, 0.1])
        
        # UI Control Areas
        self.ax_year = self.fig.add_axes([0.02, 0.7, 0.08, 0.15], facecolor='#222222')
        self.ax_month = self.fig.add_axes([0.02, 0.3, 0.08, 0.35], facecolor='#222222')
        self.ax_refresh = self.fig.add_axes([0.02, 0.1, 0.08, 0.05])
        
        self.radio_year = RadioButtons(self.ax_year, [str(y) for y in self.years], active=0, activecolor='#00d4ff')
        self.radio_month = RadioButtons(self.ax_month, self.months, active=0, activecolor='#00d4ff')
        self.btn_refresh = Button(self.ax_refresh, 'REFRESH', color='#333333', hovercolor='#444444')
        
        self.radio_year.on_clicked(self.change_year)
        self.radio_month.on_clicked(self.change_month)
        self.btn_refresh.on_clicked(self.refresh)
        
        self.update_dashboard()

    def change_year(self, label):
        self.year = int(label)
        self.update_dashboard()

    def change_month(self, label):
        self.month = self.months.index(label)
        self.update_dashboard()

    def refresh(self, event):
        self.update_dashboard()

    def get_where_clause(self, year, month):
        if month == 0:
            return f"d.year = {year}"
        else:
            return f"d.year = {year} AND d.month = {month}"

    def update_dashboard(self):
        self.fig.clear(keep_observers=True)
        self.render_plots()
        plt.draw()

    def render_plots(self):
        where = self.get_where_clause(self.year, self.month)
        
        prev_year = self.year
        prev_month = self.month - 1
        if prev_month < 0: 
             prev_month = 0
             prev_year = self.year - 1
        elif prev_month == 0: 
             # Let's say Jan vs Dec
             prev_month = 12
             prev_year = self.year - 1
        
        prev_where = self.get_where_clause(prev_year, prev_month)

        def get_kpis(w):
            sql = f"""
            SELECT SUM(total_amount) as revenue, COUNT(DISTINCT o_id) as orders,
                   COUNT(DISTINCT customer_sk) as customers, AVG(total_amount) as aov
            FROM fact_sales fs JOIN dim_date d ON fs.date_id = d.date_id WHERE {w}
            """
            return query(sql)

        kpi = get_kpis(where)
        prev_kpi = get_kpis(prev_where)
        
        def calc_delta(curr, prev):
            if not prev or prev == 0: return ""
            delta = ((curr - prev) / prev) * 100
            return f" ({'+' if delta >=0 else ''}{delta:.1f}%)"

        # Check if data exists
        if kpi.empty:
            self.fig.text(0.5, 0.5, "NO DATA FOUND OR DATABASE ERROR\nCheck your Postgres connection", 
                          fontsize=20, ha='center', color='red')
            return

        rev = kpi['revenue'][0] if not pd.isna(kpi['revenue'][0]) else 0
        ord_count = kpi['orders'][0] if not pd.isna(kpi['orders'][0]) else 0
        cust = kpi['customers'][0] if not pd.isna(kpi['customers'][0]) else 0
        aov = kpi['aov'][0] if not pd.isna(kpi['aov'][0]) else 0

        p_rev = prev_kpi['revenue'][0] if not prev_kpi.empty and not pd.isna(prev_kpi['revenue'][0]) else 0
        p_ord = prev_kpi['orders'][0] if not prev_kpi.empty and not pd.isna(prev_kpi['orders'][0]) else 0
        p_aov = prev_kpi['aov'][0] if not prev_kpi.empty and not pd.isna(prev_kpi['aov'][0]) else 0

        # KPI Layout (Top Row)
        self.fig.text(0.15, 0.95, "E-COMMERCE PERFORMANCE DASHBOARD", fontsize=20, fontweight='bold', color='#00d4ff')
        
        self.fig.text(0.15, 0.9, f"Revenue: ${rev:,.0f}{calc_delta(rev, p_rev)}", fontsize=14)
        self.fig.text(0.35, 0.9, f"Orders: {ord_count:,}{calc_delta(ord_count, p_ord)}", fontsize=14)
        self.fig.text(0.55, 0.9, f"Customers: {cust:,}", fontsize=14)
        self.fig.text(0.75, 0.9, f"AOV: ${aov:,.2f}{calc_delta(aov, p_aov)}", fontsize=14)

        # Subplots
        # 1. Revenue Trend
        ax1 = self.fig.add_subplot(self.gs[1, 1:3])
        trend_sql = f"""
        SELECT d.full_date, SUM(fs.total_amount) as revenue
        FROM fact_sales fs
        JOIN dim_date d ON fs.date_id = d.date_id
        WHERE {where}
        GROUP BY d.full_date ORDER BY d.full_date
        """
        trend = query(trend_sql)
        if not trend.empty:
            sns.lineplot(data=trend, x='full_date', y='revenue', ax=ax1, color='#00d4ff', marker='o')
            ax1.fill_between(trend['full_date'], trend['revenue'], alpha=0.2, color='#00d4ff')
        ax1.set_title("Revenue Trend Over Time", fontsize=12)
        plt.setp(ax1.get_xticklabels(), rotation=45)

        # 2. Top Products
        ax2 = self.fig.add_subplot(self.gs[1, 3])
        prod_sql = f"""
        SELECT p.pname, SUM(fs.total_amount) as revenue
        FROM fact_sales fs
        JOIN dim_product p ON fs.product_sk = p.product_sk
        JOIN dim_date d ON fs.date_id = d.date_id
        WHERE {where}
        GROUP BY p.pname ORDER BY revenue DESC LIMIT 5
        """
        products = query(prod_sql)
        if not products.empty:
            sns.barplot(data=products, y='pname', x='revenue', ax=ax2, hue='pname', palette='viridis', legend=False)
        ax2.set_title("Top 5 Products", fontsize=12)

        # 3. Category Distribution
        ax3 = self.fig.add_subplot(self.gs[2, 1])
        cat_sql = f"""
        SELECT p.category, SUM(fs.total_amount) as revenue
        FROM fact_sales fs
        JOIN dim_product p ON fs.product_sk = p.product_sk
        JOIN dim_date d ON fs.date_id = d.date_id
        WHERE {where}
        GROUP BY p.category"""
        category = query(cat_sql)
        if not category.empty:
            ax3.pie(category['revenue'], labels=category['category'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
        ax3.set_title("Revenue by Category", fontsize=12)

        # 4. Payment Status
        ax4 = self.fig.add_subplot(self.gs[2, 2])
        pay_sql = f"""
        SELECT payment_status, COUNT(*) as count
        FROM fact_payment fp
        JOIN dim_date d ON fp.date_id = d.date_id
        WHERE {where}
        GROUP BY payment_status
        """
        payment = query(pay_sql)
        if not payment.empty:
            ax4.pie(payment['count'], labels=payment['payment_status'], autopct='%1.1f%%', wedgeprops=dict(width=0.4), colors=['#2ecc71', '#e74c3c', '#f1c40f'])
        ax4.set_title("Payment Success Rate", fontsize=12)

        # 5. Orders by Gender
        ax5 = self.fig.add_subplot(self.gs[2, 3])
        gender_sql = f"""
        SELECT c.gender, COUNT(*) as count
        FROM fact_sales fs
        JOIN dim_customer c ON fs.customer_sk = c.customer_sk
        JOIN dim_date d ON fs.date_id = d.date_id
        WHERE {where}
        GROUP BY c.gender
        """
        gender = query(gender_sql)
        if not gender.empty:
            sns.barplot(data=gender, x='gender', y='count', ax=ax5, hue='gender', palette='magma', legend=False)
        ax5.set_title("Orders by Customer Gender", fontsize=12)

        plt.tight_layout(rect=[0.1, 0, 1, 0.95])

if __name__ == "__main__":
    dash = EcommerceDashboard()
    plt.show()