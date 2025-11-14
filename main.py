# main.py
import kivy

kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp
import os
import sys
import csv
from datetime import datetime

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import database
    import charts

    print("✅ Modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure database.py and charts.py are in the same folder")

# Fixed KV layout with correct color formats
kv_content = """
# expense.kv - Fixed version
<CustomButton@Button>:
    background_color: 0.2, 0.6, 0.8, 1
    background_normal: ''
    color: 1, 1, 1, 1
    font_size: '16sp'
    bold: True
    size_hint_y: None
    height: '50dp'

<ExpenseRow@BoxLayout>:
    expense_id: 0
    date: ''
    category: ''
    description: ''
    amount: 0
    size_hint_y: None
    height: '60dp'
    padding: [10, 5]
    spacing: 10
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]

    Label:
        id: date_label
        text: root.date
        size_hint_x: 0.2
        text_size: self.size
        halign: 'center'
        valign: 'middle'
        bold: True

    Label:
        id: category_label
        text: root.category
        size_hint_x: 0.25
        text_size: self.size
        halign: 'center'
        valign: 'middle'

    Label:
        id: desc_label
        text: root.description
        size_hint_x: 0.25
        text_size: self.size
        halign: 'center'
        valign: 'middle'

    Label:
        id: amount_label
        text: '${:.2f}'.format(root.amount)
        size_hint_x: 0.2
        text_size: self.size
        halign: 'center'
        valign: 'middle'
        bold: True

    Button:
        text: '×'
        size_hint_x: 0.1
        background_color: 0.8, 0.2, 0.2, 1
        background_normal: ''
        color: 1, 1, 1, 1
        bold: True
        on_press: root.delete_expense(root.expense_id)

<ExpenseScreen>:
    orientation: 'vertical'
    padding: [20, 20]
    spacing: 15
    canvas.before:
        Color:
            rgba: 0.97, 0.97, 0.97, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: '💸 Smart Expense Tracker'
        font_size: '24sp'
        bold: True
        size_hint_y: None
        height: '60dp'
        color: 0.2, 0.4, 0.6, 1

    BoxLayout:
        size_hint_y: None
        height: '50dp'
        spacing: 10

        TextInput:
            id: date_input
            hint_text: 'Date (YYYY-MM-DD)'
            readonly: False
            size_hint_x: 0.5
            background_color: 1, 1, 1, 1
            foreground_color: 0, 0, 0, 1

        TextInput:
            id: category_input
            hint_text: 'Category'
            size_hint_x: 0.5
            background_color: 1, 1, 1, 1
            foreground_color: 0, 0, 0, 1

    BoxLayout:
        size_hint_y: None
        height: '50dp'
        spacing: 10

        TextInput:
            id: amount_input
            hint_text: 'Amount'
            size_hint_x: 0.5
            input_filter: 'float'
            background_color: 1, 1, 1, 1
            foreground_color: 0, 0, 0, 1

        TextInput:
            id: desc_input
            hint_text: 'Description'
            size_hint_x: 0.5
            background_color: 1, 1, 1, 1
            foreground_color: 0, 0, 0, 1

    BoxLayout:
        size_hint_y: None
        height: '50dp'
        spacing: 10

        CustomButton:
            text: '➕ Add Expense'
            background_color: 0.2, 0.7, 0.3, 1
            on_press: root.add_expense()

        CustomButton:
            text: '📊 Charts'
            background_color: 0.3, 0.5, 0.8, 1
            on_press: root.show_chart_dialog()

    BoxLayout:
        size_hint_y: None
        height: '50dp'
        spacing: 10

        CustomButton:
            text: '📁 Export CSV'
            background_color: 0.8, 0.5, 0.2, 1
            on_press: root.export_csv()

        CustomButton:
            text: '🔄 Refresh'
            background_color: 0.5, 0.5, 0.5, 1
            on_press: root.refresh_list()

    Label:
        id: message_label
        size_hint_y: None
        height: '30dp'
        text: 'Ready to track expenses!'
        color: 0.2, 0.5, 0.8, 1
        text_size: self.size
        halign: 'center'
        valign: 'middle'

    Label:
        text: 'Recent Expenses'
        font_size: '18sp'
        bold: True
        size_hint_y: None
        height: '40dp'
        color: 0.3, 0.3, 0.3, 1

    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        bar_width: '10dp'
        bar_color: 0.2, 0.6, 0.8, 1

        GridLayout:
            id: list_container
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: 8
            padding: [5, 5]
"""

# Load the KV layout
try:
    Builder.load_string(kv_content)
    print("✅ KV layout loaded successfully")
except Exception as e:
    print(f"❌ Error loading KV layout: {e}")


class ExpenseRow(BoxLayout):
    expense_id = NumericProperty(0)
    date = StringProperty("")
    category = StringProperty("")
    description = StringProperty("")
    amount = NumericProperty(0.0)

    def __init__(self, expense_tuple, **kwargs):
        super().__init__(**kwargs)
        try:
            self.expense_id, date, category, desc, amount = expense_tuple
            self.date = date
            self.category = category
            self.description = desc
            self.amount = amount

            # Set amount color based on value
            if hasattr(self, 'ids') and 'amount_label' in self.ids:
                if amount > 100:
                    self.ids.amount_label.color = (0.9, 0.2, 0.2, 1)  # Red for high amounts
                else:
                    self.ids.amount_label.color = (0.2, 0.6, 0.2, 1)  # Green for low amounts

        except Exception as e:
            print(f"Error creating ExpenseRow: {e}")

    def delete_expense(self, expense_id):
        try:
            if database.db.delete_expense(expense_id):
                App.get_running_app().root.show_message("Expense deleted successfully!", "success")
                App.get_running_app().root.refresh_list()
            else:
                App.get_running_app().root.show_message("Error deleting expense!", "error")
        except Exception as e:
            print(f"Error deleting expense: {e}")
            App.get_running_app().root.show_message("Error deleting expense!", "error")


class ExpenseScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("✅ ExpenseScreen initialized")

        # Set default date
        self.ids.date_input.text = datetime.now().strftime("%Y-%m-%d")

        # Initialize with delay
        Clock.schedule_once(self.initialize_app, 0.5)

    def initialize_app(self, dt):
        """Initialize app components with delay"""
        try:
            print("🔄 Initializing database...")
            database.db._init_db()
            print("✅ Database initialized")

            self.refresh_list()
            self.show_message("App loaded successfully! Add your first expense.", "success")

        except Exception as e:
            error_msg = f"Initialization error: {e}"
            print(f"❌ {error_msg}")
            self.show_message(error_msg, "error")

    def add_expense(self):
        """Add new expense with validation."""
        try:
            date = self.ids.date_input.text.strip()
            category = self.ids.category_input.text.strip()
            desc = self.ids.desc_input.text.strip()
            amount_text = self.ids.amount_input.text.strip()

            # Validation
            if not all([date, category, amount_text]):
                self.show_message("Please fill all required fields!", "error")
                return

            # Date validation
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                self.show_message("Invalid date format! Use YYYY-MM-DD", "error")
                return

            # Amount validation
            try:
                amount = float(amount_text)
                if amount <= 0:
                    self.show_message("Amount must be positive!", "error")
                    return
            except ValueError:
                self.show_message("Amount must be a valid number!", "error")
                return

            # Insert into database
            expense_id = database.db.insert_expense(date, category, desc, amount)
            if expense_id:
                self.show_message("Expense added successfully!", "success")
                # Clear inputs but keep date
                self.ids.category_input.text = ""
                self.ids.desc_input.text = ""
                self.ids.amount_input.text = ""
                self.refresh_list()
            else:
                self.show_message("Error adding expense!", "error")

        except Exception as e:
            print(f"Error adding expense: {e}")
            self.show_message("Error adding expense!", "error")

    def refresh_list(self):
        """Refresh the expenses list."""
        try:
            container = self.ids.list_container
            container.clear_widgets()

            rows = database.db.fetch_all()
            if not rows:
                # Show empty state
                empty_label = Label(
                    text="No expenses yet!\\nAdd your first expense above.",
                    font_size='16sp',
                    color=(0.5, 0.5, 0.5, 1),
                    text_size=(None, None),
                    halign='center',
                    valign='middle',
                    size_hint_y=None,
                    height=dp(100)
                )
                container.add_widget(empty_label)
                return

            for row in rows:
                try:
                    container.add_widget(ExpenseRow(row))
                except Exception as e:
                    print(f"Error adding expense row: {e}")
                    continue

        except Exception as e:
            print(f"Error refreshing list: {e}")

    def show_chart_dialog(self):
        """Show chart options dialog."""
        try:
            self.show_message("Chart feature would open here. Install matplotlib for charts.", "info")
        except Exception as e:
            print(f"Error showing chart dialog: {e}")
            self.show_message("Error opening chart options!", "error")

    def export_csv(self):
        """Export expenses to CSV with professional formatting."""
        try:
            rows = database.db.fetch_all()
            if not rows:
                self.show_message("No data to export!", "warning")
                return

            # Create exports directory
            export_dir = "exports"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_export_{timestamp}.csv"
            filepath = os.path.join(export_dir, filename)

            with open(filepath, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["ID", "Date", "Category", "Description", "Amount", "Export Date"])

                # Write data
                for row in rows:
                    writer.writerow([*row, datetime.now().strftime("%Y-%m-%d")])

            self.show_message(f"Exported {len(rows)} expenses to {filename}", "success")

        except Exception as e:
            print(f"Error exporting CSV: {e}")
            self.show_message(f"Export failed: {str(e)}", "error")

    def show_message(self, message: str, msg_type: str = "info"):
        """Show styled message to user."""
        try:
            colors = {
                "success": (0.2, 0.7, 0.3, 1),  # Green
                "error": (0.9, 0.2, 0.2, 1),  # Red
                "warning": (0.9, 0.6, 0.2, 1),  # Orange
                "info": (0.2, 0.5, 0.8, 1)  # Blue
            }

            if hasattr(self, 'ids') and 'message_label' in self.ids:
                self.ids.message_label.text = message
                self.ids.message_label.color = colors.get(msg_type, colors["info"])

                # Clear message after 3 seconds
                Clock.schedule_once(lambda dt: setattr(self.ids.message_label, 'text', ''), 3)
        except Exception as e:
            print(f"Error showing message: {e}")


class SmartExpenseApp(App):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Smart Expense Tracker"

    def build(self):
        """Build and return the root widget."""
        try:
            print("Building application...")
            screen = ExpenseScreen()
            print("Application built successfully")
            return screen
        except Exception as e:
            print(f"Error building application: {e}")
            # Return a simple error screen if build fails
            error_layout = BoxLayout(orientation='vertical', padding=20)
            error_layout.add_widget(Label(
                text=f"Application Error:\\n{str(e)}",
                color=(1, 0, 0, 1),
                text_size=(400, None)
            ))
            return error_layout

    def on_start(self):
        """Called when the application starts."""
        print("Application started successfully")

    def on_stop(self):
        """Cleanup when app closes."""
        print("Application closing...")


if __name__ == "__main__":
    try:
        print("=" * 50)
        print("Starting Smart Expense Tracker...")
        print("=" * 50)

        app = SmartExpenseApp()
        app.run()

    except Exception as e:
        print(f"💥 Fatal error: {e}")
        import traceback

        traceback.print_exc()
        input("Press Enter to exit...")