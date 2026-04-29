import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

expenses = []
data_file = "expenses.json"

def load_expenses():
    global expenses
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as file:
                expenses = json.load(file)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            expenses = []
    else:
        expenses = []

def save_expenses():
    try:
        with open(data_file, 'w', encoding='utf-8') as file:
            json.dump(expenses, file, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")

def validate_amount(amount_str):
    try:
        amount = float(amount_str)
        if amount <= 0:
            return False, "Сумма должна быть положительным числом"
        return True, amount
    except ValueError:
        return False, "Сумма должна быть числом"

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, date_str
    except ValueError:
        return False, "Дата должна быть в формате ГГГГ-ММ-ДД"

def refresh_table(tree, category_filter=None, date_filter=None):
    try:
        for item in tree.get_children():
            tree.delete(item)
        
        filtered_expenses = expenses
        if category_filter and category_filter != "Все":
            filtered_expenses = [e for e in expenses if e.get('category') == category_filter]
        if date_filter:
            filtered_expenses = [e for e in filtered_expenses if e.get('date') == date_filter]
        
        for expense in filtered_expenses:
            tree.insert('', 'end', values=(expense.get('amount', 0), expense.get('category', ''), expense.get('date', '')))
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")

def calculate_total(tree):
    total = 0
    try:
        for item in tree.get_children():
            values = tree.item(item, 'values')
            if values and len(values) > 0:
                total += float(values[0])
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
    return total

def add_expense(amount_entry, category_var, date_entry, tree, total_label):
    try:
        amount_str = amount_entry.get()
        category = category_var.get()
        date_str = date_entry.get()
        
        is_valid_amount, amount = validate_amount(amount_str)
        if not is_valid_amount:
            messagebox.showerror("Ошибка", amount)
            return
        
        is_valid_date, date = validate_date(date_str)
        if not is_valid_date:
            messagebox.showerror("Ошибка", date)
            return
        
        expenses.append({'amount': amount, 'category': category, 'date': date})
        save_expenses()
        
        refresh_table(tree)
        total_label.config(text=f"Сумма: {calculate_total(tree)} руб.")
        
        amount_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        messagebox.showinfo("Успех", "Расход добавлен!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось добавить расход: {str(e)}")

def filter_expenses(tree, total_label, category_filter_var, date_filter_entry):
    try:
        category = category_filter_var.get()
        date = date_filter_entry.get()
        
        if date:
            is_valid, error = validate_date(date)
            if not is_valid:
                messagebox.showerror("Ошибка", error)
                return
        
        refresh_table(tree, category, date)
        total_label.config(text=f"Сумма: {calculate_total(tree)} руб.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при фильтрации: {str(e)}")

def calculate_period_total(date_from_entry, date_to_entry):
    try:
        date_from = date_from_entry.get()
        date_to = date_to_entry.get()
        
        if not date_from or not date_to:
            messagebox.showwarning("Ошибка", "Введите обе даты")
            return
        
        is_valid_from, error_from = validate_date(date_from)
        if not is_valid_from:
            messagebox.showerror("Ошибка", error_from)
            return
        
        is_valid_to, error_to = validate_date(date_to)
        if not is_valid_to:
            messagebox.showerror("Ошибка", error_to)
            return
        
        total = 0
        for expense in expenses:
            if expense.get('date', '') and date_from <= expense['date'] <= date_to:
                total += expense.get('amount', 0)
        
        messagebox.showinfo("Результат", f"Сумма расходов за период\n{date_from} - {date_to}\n\n{total} руб.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")

def create_gui():
    try:
        root = tk.Tk()
        root.title("Expense Tracker")
        root.geometry("800x600")
        
        category_var = tk.StringVar(value="еда")
        category_filter_var = tk.StringVar(value="Все")
        
        frame = ttk.LabelFrame(root, text="Добавить расход", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame, text="Сумма:").grid(row=0, column=0)
        amount_entry = ttk.Entry(frame, width=20)
        amount_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame, text="Категория:").grid(row=0, column=2, padx=(10,0))
        categories = ["еда", "транспорт", "развлечения"]
        category_combo = ttk.Combobox(frame, textvariable=category_var, values=categories, width=15)
        category_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=(10,0))
        date_entry = ttk.Entry(frame, width=15)
        date_entry.grid(row=0, column=5, padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        btn_add = ttk.Button(frame, text="Добавить расход", 
                             command=lambda: add_expense(amount_entry, category_var, date_entry, tree, total_label))
        btn_add.grid(row=1, column=0, columnspan=6, pady=10)
        
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0)
        filter_categories = ["Все", "еда", "транспорт", "развлечения"]
        filter_combo = ttk.Combobox(filter_frame, textvariable=category_filter_var, values=filter_categories, width=15)
        filter_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=2, padx=(10,0))
        date_filter_entry = ttk.Entry(filter_frame, width=15)
        date_filter_entry.grid(row=0, column=3, padx=5)
        
        btn_filter = ttk.Button(filter_frame, text="Применить фильтр",
                               command=lambda: filter_expenses(tree, total_label, category_filter_var, date_filter_entry))
        btn_filter.grid(row=0, column=4, padx=10)
        
        period_frame = ttk.LabelFrame(root, text="Подсчёт суммы за период", padding=10)
        period_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(period_frame, text="Дата с:").grid(row=0, column=0)
        date_from_entry = ttk.Entry(period_frame, width=15)
        date_from_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(period_frame, text="по:").grid(row=0, column=2, padx=(10,0))
        date_to_entry = ttk.Entry(period_frame, width=15)
        date_to_entry.grid(row=0, column=3, padx=5)
        
        btn_period = ttk.Button(period_frame, text="Подсчитать сумму",
                               command=lambda: calculate_period_total(date_from_entry, date_to_entry))
        btn_period.grid(row=0, column=4, padx=10)
        
        table_frame = ttk.Frame(root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(table_frame, columns=('amount', 'category', 'date'), show='headings', height=15)
        tree.heading('amount', text='Сумма')
        tree.heading('category', text='Категория')
        tree.heading('date', text='Дата')
        tree.column('amount', width=150)
        tree.column('category', width=150)
        tree.column('date', width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        total_label = ttk.Label(bottom_frame, text="Сумма: 0 руб.", font=('Arial', 12, 'bold'))
        total_label.pack()
        
        load_expenses()
        refresh_table(tree)
        total_label.config(text=f"Сумма: {calculate_total(tree)} руб.")
        
        return root
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать интерфейс: {str(e)}")
        raise

def main():
    try:
        root = create_gui()
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    main()
