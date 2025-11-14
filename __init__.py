"""
Smart Expense Tracker - A professional expense tracking application
Built with Kivy, SQLite, and Matplotlib

Features:
- Add, view, and delete expenses
- Beautiful and intuitive UI
- Multiple chart types (Bar, Pie, Line)
- CSV export functionality
- Date picker for easy date selection
- Category-wise spending analysis
- Cross-platform (Windows, Android, Linux, macOS)

Author: Your Name
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"

# Package imports for easier access
from .database import DatabaseManager, db
from .charts import ChartGenerator, chart_gen, show_category_chart_for_month
from .main import SmartExpenseApp, ExpenseScreen, ExpenseRow, ChartDialog

# Define what gets imported with "from package import *"
__all__ = [
    # Database
    'DatabaseManager',
    'db',

    # Charts
    'ChartGenerator',
    'chart_gen',
    'show_category_chart_for_month',

    # Main application
    'SmartExpenseApp',
    'ExpenseScreen',
    'ExpenseRow',
    'ChartDialog',

    # Constants
    '__version__',
    '__author__',
]


# Package initialization
def init_package():
    """Initialize the package - can be used for setup tasks"""
    print(f"Smart Expense Tracker v{__version__} initialized")
    print("Package ready to use!")

# Optional: Auto-initialize when package is imported
# init_package()