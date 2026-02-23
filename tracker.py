

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import hashlib
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import xlsxwriter

class Database:
    def __init__(self, db_name='expense_tracker.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            password_hash = self.hash_password(password)
            cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                         (username, password_hash, email))
            conn.commit()
            return True, "User created successfully!"
        except sqlite3.IntegrityError:
            return False, "Username already exists!"
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute('SELECT id, username FROM users WHERE username = ? AND password_hash = ?',
                      (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        return user if user else None

class ExpenseTracker:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
    
    def add_expense(self, date, category, amount, description=''):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (user_id, date, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.user_id, date, category, amount, description))
        conn.commit()
        conn.close()
        return True
    
    def get_expenses(self):
        conn = self.db.get_connection()
        query = '''
            SELECT id, date, category, amount, description, created_at
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC
        '''
        df = pd.read_sql_query(query, conn, params=(self.user_id,))
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def get_filtered_expenses(self, filter_category=None, days=None):
        df = self.get_expenses()
        
        if not df.empty:
            if filter_category and filter_category != 'All':
                df = df[df['category'] == filter_category]
            
            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                df = df[df['date'] >= cutoff_date]
        
        return df
    
    def get_category_summary(self):
        df = self.get_expenses()
        if df.empty:
            return pd.DataFrame()
        
        summary = df.groupby('category')['amount'].agg(['sum', 'count'])
        summary.columns = ['Total', 'Count']
        summary['Percentage'] = (summary['Total'] / summary['Total'].sum() * 100).round(2)
        return summary.sort_values('Total', ascending=False)
    
    def get_monthly_data(self, month, year):
        df = self.get_expenses()
        if df.empty:
            return pd.DataFrame()
        
        mask = (df['date'].dt.month == month) & (df['date'].dt.year == year)
        return df[mask]
    
    def delete_expense(self, expense_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', 
                      (expense_id, self.user_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

class ReportExporter:
    @staticmethod
    def export_to_excel(df, filename='expense_report.xlsx'):
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export = df.copy()
            df_export['date'] = df_export['date'].dt.strftime('%Y-%m-%d')
            df_export.to_excel(writer, sheet_name='Expenses', index=False)

            if not df.empty:
                summary = df.groupby('category')['amount'].sum().reset_index()
                summary.columns = ['Category', 'Total Amount']
                summary.to_excel(writer, sheet_name='Summary', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Expenses']
            
            money_format = workbook.add_format({'num_format': '$#,##0.00'})
            worksheet.set_column('D:D', 12, money_format)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_to_pdf(df, month_name, year, total_spent, num_transactions):
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        title = Paragraph(f"<b>Expense Report - {month_name} {year}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))

        summary_text = f"""
        <b>Summary:</b><br/>
        Total Spent: ${total_spent:,.2f}<br/>
        Number of Transactions: {num_transactions}<br/>
        Average Transaction: ${total_spent/num_transactions if num_transactions > 0 else 0:.2f}
        """
        summary = Paragraph(summary_text, styles['Normal'])
        elements.append(summary)
        elements.append(Spacer(1, 20))

        if not df.empty:
            df_display = df.copy()
            df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d')
            df_display['amount'] = df_display['amount'].apply(lambda x: f"${x:.2f}")
            
            table_data = [['Date', 'Category', 'Amount', 'Description']]
            for _, row in df_display.iterrows():
                table_data.append([
                    row['date'],
                    row['category'],
                    row['amount'],
                    row['description'][:30] if row['description'] else ''
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        doc.build(elements)
        output.seek(0)
        return output


def login_page():
    st.markdown('<h1 class="main-header">🔐 Expense Tracker Login</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    user = st.session_state.db.authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please fill in all fields")
    
    with tab2:
        st.subheader("Create a new account")
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_username")
            new_email = st.text_input("Email (optional)", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup = st.form_submit_button("Sign Up", use_container_width=True)
            
            if signup:
                if new_username and new_password:
                    if new_password == confirm_password:
                        success, message = st.session_state.db.create_user(
                            new_username, new_password, new_email
                        )
                        if success:
                            st.success(message + " Please login.")
                        else:
                            st.error(message)
                    else:
                        st.error("Passwords don't match")
                else:
                    st.warning("Please fill in all required fields")


def main():
    st.set_page_config(page_title="Expense Tracker Pro", page_icon="💰", layout="wide")
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'db' not in st.session_state:
        st.session_state.db = Database()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
        return

    if 'tracker' not in st.session_state or st.session_state.get('current_user_id') != st.session_state.user_id:
        st.session_state.tracker = ExpenseTracker(st.session_state.db, st.session_state.user_id)
        st.session_state.current_user_id = st.session_state.user_id
    
    tracker = st.session_state.tracker

    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<h1 class="main-header">💰 Expense Tracker Pro</h1>', unsafe_allow_html=True)
    with col2:
        st.write(f"👤 {st.session_state.username}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Add Expense", "View Expenses", "Analytics", "Monthly Report", "Export Data"])

    categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other']

    if page == "Dashboard":
        st.header("📈 Dashboard Overview")
        
        expenses_df = tracker.get_expenses()
        
        if expenses_df.empty:
            st.info("No expenses recorded yet. Start by adding your first expense!")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            total_spent = expenses_df['amount'].sum()
            num_transactions = len(expenses_df)
            avg_transaction = total_spent / num_transactions if num_transactions > 0 else 0
            last_30_days = tracker.get_filtered_expenses(days=30)
            last_30_days_total = last_30_days['amount'].sum() if not last_30_days.empty else 0

            with col1:
                st.metric("Total Spent", f"${total_spent:,.2f}")
            with col2:
                st.metric("Transactions", num_transactions)
            with col3:
                st.metric("Avg Transaction", f"${avg_transaction:.2f}")
            with col4:
                st.metric("Last 30 Days", f"${last_30_days_total:,.2f}")
            
            st.divider()

            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Spending by Category")
                category_totals = expenses_df.groupby('category')['amount'].sum()
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                ax1.pie(category_totals.values, labels=category_totals.index, autopct='%1.1f%%', startangle=90)
                ax1.set_title('Category Distribution')
                st.pyplot(fig1)
            
            with col2:
                st.subheader("Recent Spending Trend")
                daily_spending = expenses_df.groupby(expenses_df['date'].dt.date)['amount'].sum().tail(30)
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                ax2.plot(daily_spending.index, daily_spending.values, marker='o', linestyle='-', linewidth=2)
                ax2.set_xlabel('Date')
                ax2.set_ylabel('Amount ($)')
                ax2.set_title('Daily Spending (Last 30 Days)')
                ax2.tick_params(axis='x', rotation=45)
                ax2.grid(True, alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig2)

    elif page == "Add Expense":
        st.header("➕ Add New Expense")
        
        with st.form("add_expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                expense_date = st.date_input("Date", datetime.now())
                category = st.selectbox("Category", categories)
            
            with col2:
                amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
                description = st.text_input("Description (optional)")
            
            submitted = st.form_submit_button("Add Expense", use_container_width=True)
            
            if submitted:
                if amount > 0:
                    tracker.add_expense(expense_date, category, amount, description)
                    st.success(f"✅ Added ${amount:.2f} for {category}")
                    st.balloons()
                else:
                    st.error("Amount must be greater than 0")

    elif page == "View Expenses":
        st.header("📋 View Expenses")
        
        expenses_df = tracker.get_expenses()
        
        if expenses_df.empty:
            st.info("No expenses to display.")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_category = st.selectbox("Filter by Category", ['All'] + categories)
            
            with col2:
                filter_days = st.selectbox("Time Period", 
                                         ['All Time', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days'])
                days_map = {'All Time': None, 'Last 7 Days': 7, 'Last 30 Days': 30, 'Last 90 Days': 90}
                days = days_map[filter_days]
            
            with col3:
                sort_by = st.selectbox("Sort by", ['Date (Newest)', 'Date (Oldest)', 'Amount (High-Low)', 'Amount (Low-High)'])

            filtered_df = tracker.get_filtered_expenses(
                filter_category=filter_category if filter_category != 'All' else None,
                days=days
            )
            
            if not filtered_df.empty:
                if sort_by == 'Date (Newest)':
                    filtered_df = filtered_df.sort_values('date', ascending=False)
                elif sort_by == 'Date (Oldest)':
                    filtered_df = filtered_df.sort_values('date', ascending=True)
                elif sort_by == 'Amount (High-Low)':
                    filtered_df = filtered_df.sort_values('amount', ascending=False)
                else:
                    filtered_df = filtered_df.sort_values('amount', ascending=True)
                
                st.metric("Total", f"${filtered_df['amount'].sum():,.2f}")

                display_df = filtered_df.copy()
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
                
                st.dataframe(
                    display_df[['id', 'date', 'category', 'amount', 'description']],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.divider()
                with st.expander("🗑️ Delete an Expense"):
                    delete_id = st.number_input("Enter expense ID to delete", min_value=1, step=1)
                    if st.button("Delete Expense"):
                        if tracker.delete_expense(delete_id):
                            st.success("Expense deleted!")
                            st.rerun()
                        else:
                            st.error("Invalid ID or permission denied")
            else:
                st.info("No expenses match the selected filters.")

    elif page == "Analytics":
        st.header("📊 Analytics & Insights")
        
        expenses_df = tracker.get_expenses()
        
        if expenses_df.empty:
            st.info("No data available for analysis.")
        else:
            st.subheader("Category Breakdown")
            summary = tracker.get_category_summary()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(summary, use_container_width=True)
            
            with col2:
                top_category = summary.index[0]
                top_amount = summary.iloc[0]['Total']
                st.metric("Top Category", top_category)
                st.metric("Amount", f"${top_amount:,.2f}")
            
            st.divider()

            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Category Comparison")
                fig3, ax3 = plt.subplots(figsize=(8, 6))
                summary['Total'].sort_values(ascending=True).plot(kind='barh', ax=ax3, color='steelblue')
                ax3.set_xlabel('Amount ($)')
                ax3.set_title('Total Spending by Category')
                st.pyplot(fig3)
            
            with col2:
                st.subheader("Monthly Trend")
                monthly_spending = expenses_df.groupby(expenses_df['date'].dt.to_period('M'))['amount'].sum()
                monthly_spending.index = monthly_spending.index.astype(str)
                fig4, ax4 = plt.subplots(figsize=(8, 6))
                ax4.bar(monthly_spending.index, monthly_spending.values, color='coral')
                ax4.set_xlabel('Month')
                ax4.set_ylabel('Amount ($)')
                ax4.set_title('Monthly Spending')
                ax4.tick_params(axis='x', rotation=45)
                st.pyplot(fig4)
    elif page == "Monthly Report":
        st.header("📅 Monthly Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1,
                                        format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
        with col2:
            selected_year = st.number_input("Year", min_value=2000, max_value=2100, value=datetime.now().year)
        
        if st.button("Generate Report", use_container_width=True):
            monthly_data = tracker.get_monthly_data(selected_month, selected_year)
            
            if monthly_data.empty:
                st.warning(f"No expenses found for {datetime(2000, selected_month, 1).strftime('%B')} {selected_year}")
            else:
                total_spent = monthly_data['amount'].sum()
                num_transactions = len(monthly_data)
                avg_transaction = total_spent / num_transactions
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Spent", f"${total_spent:,.2f}")
                with col2:
                    st.metric("Transactions", num_transactions)
                with col3:
                    st.metric("Average", f"${avg_transaction:.2f}")
                
                st.divider()
                
                st.subheader("Category Breakdown")
                category_summary = monthly_data.groupby('category')['amount'].agg(['sum', 'count'])
                category_summary.columns = ['Total', 'Count']
                category_summary['Percentage'] = (category_summary['Total'] / total_spent * 100).round(2)
                category_summary = category_summary.sort_values('Total', ascending=False)
                st.dataframe(category_summary, use_container_width=True)
                
                st.divider()
                
                st.subheader("Top 5 Expenses")
                top_expenses = monthly_data.nlargest(5, 'amount')[['date', 'category', 'amount', 'description']]
                top_expenses['date'] = top_expenses['date'].dt.strftime('%Y-%m-%d')
                top_expenses['amount'] = top_expenses['amount'].apply(lambda x: f"${x:.2f}")
                st.dataframe(top_expenses, use_container_width=True, hide_index=True)

    elif page == "Export Data":
        st.header("📥 Export Data")
        
        expenses_df = tracker.get_expenses()
        
        if expenses_df.empty:
            st.info("No data to export.")
        else:
            st.subheader("Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Export All Expenses to Excel")
                excel_file = ReportExporter.export_to_excel(expenses_df)
                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_file,
                    file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                st.write("### Export Monthly Report to PDF")
                month = st.selectbox("Select Month", range(1, 13), index=datetime.now().month - 1,
                                   format_func=lambda x: datetime(2000, x, 1).strftime('%B'), key="pdf_month")
                year = st.number_input("Year", min_value=2000, max_value=2100, value=datetime.now().year, key="pdf_year")
                
                if st.button("Generate PDF", use_container_width=True):
                    monthly_data = tracker.get_monthly_data(month, year)
                    if not monthly_data.empty:
                        month_name = datetime(2000, month, 1).strftime('%B')
                        total = monthly_data['amount'].sum()
                        count = len(monthly_data)
                        pdf_file = ReportExporter.export_to_pdf(monthly_data, month_name, year, total, count)
                        
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_file,
                            file_name=f"report_{year}_{month:02d}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.warning("No data for selected month")
    expenses_df = tracker.get_expenses()
    st.sidebar.divider()
    st.sidebar.info(f"📊 Total Expenses: {len(expenses_df)}\n💵 Total Amount: ${expenses_df['amount'].sum():,.2f}")


# Run the application
if __name__ == "__main__":
    main()
