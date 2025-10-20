# Expense Tracker Pro

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Live Demo
[Try it live here](https://expense-tracker-pro-k5xrzd2spyjrdpkjgv9q97.streamlit.app)

A full-stack expense tracking application with user authentication, SQLite database, interactive analytics, and automated report generation.

## Features

- Secure Authentication: User signup/login with SHA-256 password hashing
- Interactive Dashboard: Real-time expense analytics and visualizations
- Database Integration: SQLite backend for data persistence
- Data Visualization: Charts and graphs using Matplotlib
- Export Functionality: Generate Excel and PDF reports
- Category Tracking: Organize expenses by categories (Food, Transport, Entertainment, etc.)
- Monthly Reports: Automated financial summaries with statistics
- Advanced Filtering: Sort and filter by date, category, and amount
- Expense Management: Edit and delete transactions
- Responsive Design: Works on desktop and mobile

## Tech Stack

- Backend: Python 3.10+, SQLite
- Frontend: Streamlit
- Data Processing: Pandas, NumPy
- Visualization: Matplotlib
- Export: XlsxWriter, ReportLab
- Security: Hashlib (SHA-256)

## Local Installation

```bash
# Clone repository
git clone https://github.com/CODER-T101/expense-tracker-pro.git
cd expense-tracker-pro

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run tracker.py
```

## Usage

- Sign Up: Create a new account with username and password
- Login: Access your personalized dashboard
- Add Expenses: Record daily transactions with categories and descriptions
- View Dashboard: Monitor spending patterns with interactive charts
- Analyze Data: View category breakdowns and spending trends
- Generate Reports: Create monthly summaries with detailed statistics
- Export Data: Download reports as Excel or PDF files


## 📸 Screenshots
```
### Login & Authentication
![Login](screenshots/login.png)

### Dashboard Overview
![Dashboard](screenshots/dashboard.png)

### Expense Analytics
![Analytics](screenshots/analytics.png)

### Report Export
![Export](screenshots/export.png)
```

### Dashboard Overview
View your spending at a glance with interactive charts and key metrics.

### Analytics & Insights
Analyze spending patterns by category with visual breakdowns.

### Monthly Reports
Generate comprehensive reports with statistics and top expenses.

### Export Options
Download your financial data as Excel spreadsheets or PDF documents.

## Key Functionalities

### Dashboard
- Total spending overview
- Transaction count
- Average transaction amount
- Last 30 days spending
- Pie chart for category distribution
- Line graph for daily spending trends

### Expense Management
- Add new expenses with date, category, amount, and description
- View all expenses in a sortable table
- Filter by category and time period
- Delete individual transactions

### Analytics
- Category-wise spending breakdown
- Percentage distribution
- Bar charts for comparison
- Monthly spending trends
- Top expense identification

### Reports & Export
- Monthly summary generation
- Category breakdowns with percentages
- Top 5 expenses listing
- Excel export with multiple sheets
- Professional PDF reports with formatting

## Future Enhancements

- [ ] **PostgreSQL Migration** - Persistent cloud storage for better data retention
- [ ] **Budget Limits** - Set monthly budgets with alerts
- [ ] **Recurring Expenses** - Auto-add regular bills
- [ ] **Multi-Currency Support** - Handle international transactions
- [ ] **Dark Mode** - Theme customization
- [ ] **Email Notifications** - Monthly report delivery
- [ ] **Data Visualization Upgrade** - Interactive Plotly charts
- [ ] **CSV Import** - Bulk data upload
- [ ] **Mobile App** - Native mobile version
- [ ] **API Integration** - Connect with banking APIs
- [ ] **Expense Predictions** - ML-based spending forecasts
- [ ] **Shared Expenses** - Family/group expense tracking

## Project Structure
```
expense-tracker-pro/
│
├── tracker.py              # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
├── expense_tracker.db     # SQLite database (auto-generated)
└── screenshots/           # App screenshots (optional)
```

## Configuration

The application uses default settings that work out of the box. For custom configuration:

- **Database:** Modify `Database.__init__()` to change DB name
- **Categories:** Update `categories` list in `main()` function
- **Port:** Streamlit uses port 8501 by default

## Testing

Create a test account and try these scenarios:
1. Add 10-15 expenses across different categories
2. Generate monthly reports
3. Export data to Excel and PDF
4. Test filtering and sorting options
5. Verify data persistence after logout

## License

MIT License

Copyright (c) 2025 CODER-T101

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author

**CODER-T101**
- GitHub: [@CODER-T101](https://github.com/CODER-T101)
- Project Repository: [expense-tracker-pro](https://github.com/CODER-T101/expense-tracker-pro)
- Live Demo: [Expense Tracker Pro](https://expense-tracker-pro-k5xrzd2spyjrdpkjgv9q97.streamlit.app)

## Acknowledgments

- Built with using Python and Streamlit
- Inspired by the need for simple, effective personal finance management
- Thanks to the open-source community for amazing tools and libraries

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/CODER-T101/expense-tracker-pro/issues).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

For questions, feedback, or collaboration opportunities, feel free to reach out through GitHub.

---

**If you found this project helpful, please give it a star!**

**Made with Python 🐍 | Deployed on Streamlit ☁️ | Open Source**
