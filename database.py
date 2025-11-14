# database.py
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = "expenses.db"


class DatabaseManager:
    """Professional database manager with error handling."""

    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name

    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_name)
        return conn

    def _init_db(self):
        """Initialize database with proper error handling."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create index for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_date_category 
                ON expenses(date, category)
            ''')

            conn.commit()
            logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
        finally:
            conn.close()

    def insert_expense(self, date: str, category: str, description: str, amount: float):
        """Insert expense with validation and return ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                (date, category, description, amount)
            )
            conn.commit()
            last_id = cursor.lastrowid
            logger.info(f"Expense inserted with ID: {last_id}")
            return last_id
        except sqlite3.Error as e:
            logger.error(f"Error inserting expense: {e}")
            return None
        finally:
            conn.close()

    def fetch_all(self):
        """Fetch all expenses ordered by date."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, date, category, description, amount FROM expenses ORDER BY date DESC, id DESC"
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching expenses: {e}")
            return []
        finally:
            conn.close()

    def delete_expense(self, expense_id: int):
        """Delete expense by ID with error handling."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Expense {expense_id} deleted successfully")
            return success
        except sqlite3.Error as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            return False
        finally:
            conn.close()


# Global database instance
db = DatabaseManager()