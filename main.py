# main.py
import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
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
    import matplotlib.pyplot as plt
    import io
    from kivy.core.image import Image as CoreImage
    from kivy.uix.image import Image
    print("✅ Modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure database.py is in the same folder and matplotlib is installed")


# ---------------- KV Layout ----------------
kv_content = """
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

Builder.load_string(kv_content)


# ---------------- Chart Helpers ----------------
def fig_to_texture(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    buf.seek(0)
    img = CoreImage(buf, ext="png").texture
    plt.close(fig)
    return img


def get_category_chart():
    rows = database.db.fetch_all()
    if not rows:
        return None
    categories = {}
    for _, date, cat, desc, amount in rows:
        categories[cat] = categories.get(cat, 0) + amount
    labels = list(categories.keys())
    values = list(categories.values())
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    ax.set_title("Expenses by Category")
    return fig_to_texture(fig)


def get_month_chart():
    rows = database.db.fetch_all()
    if not rows:
        return None
    months = {}
    for _, date, cat, desc, amount in rows:
        month = date[:7]  # YYYY-MM
        months[month] = months.get(month, 0) + amount
    labels = list(months.keys())
    values = list(months.values())
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title("Monthly Expenses")
    ax.set_ylabel("Amount (MK)")
    ax.set_xticklabels(labels, rotation=30)
    return fig_to_texture(fig)


def show_chart_popup(title, texture):
    if texture is None:
        popup = Popup(title="No Data Available", size_hint=(0.8, 0.4))
        popup.open()
        return
    layout = BoxLayout()
    layout.add_widget(Image(texture=texture))
    popup = Popup(title=title, size_hint=(0.9, 0.9))
    popup.add_widget(layout)
    popup.open()


# ---------------- ExpenseRow ----------------
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
            if hasattr(self, 'ids') and 'amount_label' in self.ids:
                self.ids.amount_label.color = (0.9, 0.2, 0.2, 1) if amount > 100 else (0.2, 0.6, 0.2, 1)
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


# ---------------- ExpenseScreen ----------------
class ExpenseScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_input.text = datetime.now().strftime("%Y-%m-%d")
        Clock.schedule_once(self.initialize_app, 0.5)

    def initialize_app(self, dt):
        try:
            database.db._init_db()
            self.refresh_list()
            self.show_message("App loaded successfully! Add your first expense.", "success")
        except Exception as e:
            self.show_message(f"Initialization error: {e}", "error")

    def add_expense(self):
        date = self.ids.date_input.text.strip()
        category = self.ids.category_input.text.strip()
        desc = self.ids.desc_input.text.strip()
        amount_text = self.ids.amount_input.text.strip()
        if not all([date, category, amount_text]):
            self.show_message("Please fill all required fields!", "error")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.show_message("Invalid date format! Use YYYY-MM-DD", "error")
            return
        try:
            amount = float(amount_text)
            if amount <= 0:
                self.show_message("Amount must be positive!", "error")
                return
        except ValueError:
            self.show_message("Amount must be a valid number!", "error")
            return
        expense_id = database.db.insert_expense(date, category, desc, amount)
        if expense_id:
            self.show_message("Expense added successfully!", "success")
            self.ids.category_input.text = ""
            self.ids.desc_input.text = ""
            self.ids.amount_input.text = ""
            self.refresh_list()
        else:
            self.show_message("Error adding expense!", "error")

    def refresh_list(self):
        container = self.ids.list_container
        container.clear_widgets()
        rows = database.db.fetch_all()
        if not rows:
            empty_label = Label(
                text="No expenses yet!\\nAdd your first expense above.",
                font_size='16sp',
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(100),
                halign='center',
                valign='middle'
            )
            container.add_widget(empty_label)
            return
        for row in rows:
            try:
                container.add_widget(ExpenseRow(row))
            except Exception as e:
                print(f"Error adding expense row: {e}")

    def show_chart_dialog(self):
        try:
            box = BoxLayout(orientation="vertical", spacing=10, padding=20)
            btn1 = Button(text="📊 Category Chart", size_hint_y=None, height=50)
            btn2 = Button(text="📈 Monthly Chart", size_hint_y=None, height=50)
            popup = Popup(title="Select Chart", size_hint=(0.7, 0.4))
            box.add_widget(btn1)
            box.add_widget(btn2)
            popup.add_widget(box)

            btn1.bind(on_press=lambda x: [popup.dismiss(), show_chart_popup("Expenses by Category", get_category_chart())])
            btn2.bind(on_press=lambda x: [popup.dismiss(), show_chart_popup("Monthly Spending Trend", get_month_chart())])
            popup.open()
        except Exception as e:
            print(f"Error showing charts: {e}")
            self.show_message("Error opening charts!", "error")

    def export_csv(self):
        try:
            rows = database.db.fetch_all()
            if not rows:
                self.show_message("No data to export!", "warning")
                return
            export_dir = "exports"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_export_{timestamp}.csv"
            filepath = os.path.join(export_dir, filename)
            with open(filepath, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Category", "Description", "Amount", "Export Date"])
                for row in rows:
                    writer.writerow([*row, datetime.now().strftime("%Y-%m-%d")])
            self.show_message(f"Exported {len(rows)} expenses to {filename}", "success")
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            self.show_message(f"Export failed: {str(e)}", "error")

    def show_message(self, message: str, msg_type: str = "info"):
        colors = {"success": (0.2, 0.7, 0.3, 1), "error": (0.9, 0.2, 0.2, 1),
                  "warning": (0.9, 0.6, 0.2, 1), "info": (0.2, 0.5, 0.8, 1)}
        if hasattr(self, 'ids') and 'message_label' in self.ids:
            self.ids.message_label.text = message
            self.ids.message_label.color = colors.get(msg_type, colors["info"])
            Clock.schedule_once(lambda dt: setattr(self.ids.message_label, 'text', ''), 3)


# ---------------- App ----------------
class SmartExpenseApp(App):
    def build(self):
        return ExpenseScreen()


if __name__ == "__main__":
    SmartExpenseApp().run()
