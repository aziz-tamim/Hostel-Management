import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt

FILE_PATH = "student_expense.csv"

# ------------------- Data Handling -------------------
def load_data():
    data_list = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                data_list.append(row)
    return data_list

def save_data():
    with open(FILE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Serial", "Roll", "Student", "Date", "Religion", "PrayerDone",
                         "MealCount", "Mess", "Hostel", "Electricity", "Inventory"])
        for row in data:
            writer.writerow(row)

def has_fixed_cost(roll):
    for row in data:
        if row[1] == roll and (float(row[8]) > 0 or float(row[9]) > 0 or float(row[10]) > 0):
            return True
    return False

# ------------------- Tooltip Class -------------------
# class ToolTip:
#     def __init__(self, widget, text):
#         self.widget = widget
#         self.text = text
#         self.tip_window = None
#         self.widget.bind("<Enter>", self.show_tip)
#         self.widget.bind("<Leave>", self.hide_tip)

#     def show_tip(self, event=None):
#         if self.tip_window or not self.text:
#             return
#         x, y, _, cy = self.widget.bbox("insert") or (0,0,0,0)
#         x = x + self.widget.winfo_rootx() + 25
#         y = y + cy + self.widget.winfo_rooty() + 20
#         self.tip_window = tw = tk.Toplevel(self.widget)
#         tw.wm_overrideredirect(True)
#         tw.wm_geometry(f"+{x}+{y}")
#         label = tk.Label(tw, text=self.text, justify='left',
#                          background="#ffffe0", relief='solid', borderwidth=1,
#                          font=("tahoma", "8", "normal"))
#         label.pack(ipadx=5, ipady=3)

#     def hide_tip(self, event=None):
#         if self.tip_window:
#             self.tip_window.destroy()
#         self.tip_window = None

# ------------------- Add Expense -------------------
def add_expense():
    roll = roll_entry.get().strip()
    student = student_name.get().strip()
    religion = religion_var.get()
    prayer_done = prayer_var.get()
    meal_count = meal_count_entry.get().strip()

    if not roll or not student or not religion or not prayer_done:
        messagebox.showwarning("Warning", "Roll, Student, Religion, Prayer, and Meal Count are required!")
        return

    try:
        mess = float(mess_entry.get() or 0)
        hostel = float(hostel_entry.get() or 0)
        electricity = float(electricity_entry.get() or 0)
        inventory = float(inventory_entry.get() or 0)
        meal_count = int(meal_count or 1)
    except ValueError:
        messagebox.showwarning("Warning", "Enter valid numeric values!")
        return

    if prayer_done == "No":
        meal_count += 1  # penalty 1 meal

    mess *= meal_count

    if has_fixed_cost(roll):
        hostel = electricity = inventory = 0

    date = datetime.now().strftime("%Y-%m-%d")
    serial = len(data) + 1
    data.append([serial, roll, student, date, religion, prayer_done,
                 meal_count, mess, hostel, electricity, inventory])
    save_data()
    update_table()
    messagebox.showinfo("Success", f"Expense added for Roll {roll} - {student}")
    
    # ------------------ Auto Clear Fields ------------------
    roll_entry.delete(0, tk.END)
    student_name.delete(0, tk.END)
    religion_var.set('')
    prayer_var.set('')
    meal_count_entry.delete(0, tk.END)
    mess_entry.delete(0, tk.END)
    # hostel_entry.delete(0, tk.END)
    # electricity_entry.delete(0, tk.END)
    # inventory_entry.delete(0, tk.END)

# ------------------- Update Table -------------------
def update_table():
    for row in tree.get_children():
        tree.delete(row)
    for row in data:
        tree.insert("", tk.END, values=row)

# ------------------- Show Student Summary -------------------
def show_student_summary():
    roll = summary_roll.get().strip()
    date_filter = summary_date.get().strip()
    month_filter = summary_month.get().strip()
    year_filter = summary_year.get().strip()

    if not roll:
        messagebox.showwarning("Warning", "Enter Roll number!")
        return

    # Must provide at least one filter besides roll
    if not (date_filter or month_filter or year_filter):
        messagebox.showwarning("Warning", "Enter at least Date, Month, or Year to search!")
        return

    # Filter by roll
    student_data = [row for row in data if row[1] == roll]

    # Apply optional filters
    if date_filter:
        try:
            parsed_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            student_data = [row for row in student_data if datetime.strptime(row[3], "%Y-%m-%d").date() == parsed_date]
        except ValueError:
            messagebox.showwarning("Warning", "Enter Date in YYYY-MM-DD format!")
            return

    if month_filter:
        try:
            month_int = int(month_filter)
            student_data = [row for row in student_data if datetime.strptime(row[3], "%Y-%m-%d").month == month_int]
        except ValueError:
            messagebox.showwarning("Warning", "Enter a valid Month (1-12)!")
            return
    if year_filter:
        try:
            year_int = int(year_filter)
            student_data = [row for row in student_data if datetime.strptime(row[3], "%Y-%m-%d").year == year_int]
        except ValueError:
            messagebox.showwarning("Warning", "Enter a valid Year (YYYY)!")
            return

    if not student_data:
        messagebox.showinfo("Info", "No data found for the given filter!")
        return

    # --- Remaining code same as before ---
    total_mess = total_hostel = total_electricity = total_inventory = total_penalty = 0
    student_name_val = student_data[0][2]

    for row in student_data:
        total_mess += float(row[7])
        total_hostel += float(row[8])
        total_electricity += float(row[9])
        total_inventory += float(row[10])
        if row[5] == "No":
            total_penalty += float(row[7]) / int(row[6])

    total_all = total_mess + total_hostel + total_electricity + total_inventory

    # Popup code 
    popup = tk.Toplevel(root)
    popup.title(f"{student_name_val} (Roll: {roll}) Summary")
    popup.configure(bg=theme["bg"])
    popup.geometry("400x400")

    tk.Label(popup, text=f"Expense Summary", font=("Helvetica", 14, "bold"),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=10)
    tk.Label(popup, text=f"Name: {student_name_val}", font=("Helvetica", 12),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
    tk.Label(popup, text=f"Roll: {roll}", font=("Helvetica", 12),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
    tk.Label(popup, text=f"Meal Total: {total_mess} BDT", font=("Helvetica", 12),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
    tk.Label(popup, text=f"Hostel: {total_hostel} BDT", font=("Helvetica", 12),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
    tk.Label(popup, text=f"Electricity: {total_electricity} BDT", font=("Helvetica", 12),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
    tk.Label(popup, text=f"Inventory: {total_inventory} BDT", font=("Helvetica", 12),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
    tk.Label(popup, text=f"Penalty: {total_penalty} BDT", font=("Helvetica", 12),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
    tk.Label(popup, text=f"Total: {total_all} BDT", font=("Helvetica", 12, "bold"),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=10)

    def on_popup_close():
        categories = ["Meal", "Hostel", "Electricity", "Inventory", "Penalty"]
        values = [total_mess, total_hostel, total_electricity, total_inventory, total_penalty]
        plt.bar(categories, values, color=['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0'])
        plt.title(f"{student_name_val} (Roll {roll}) Expense Summary")
        plt.ylabel("Amount (BDT)")
        plt.show()

    popup.protocol("WM_DELETE_WINDOW", lambda: (popup.destroy(), on_popup_close()))
    tk.Button(popup, text="Close", command=lambda: (popup.destroy(), on_popup_close()),
              font=("Helvetica", 12, "bold"), bg="#ff9800", fg="white", width=15).pack(pady=10)

def show_overall_chart():
    if not data:
        messagebox.showinfo("Info", "No data available to show chart!")
        return

    total_mess = total_hostel = total_electricity = total_inventory = 0

    for row in data:
        try:
            total_mess += float(row[7])
            total_hostel += float(row[8])
            total_electricity += float(row[9])
            total_inventory += float(row[10])
        except ValueError:
            continue

    categories = ["Meal", "Hostel", "Electricity", "Inventory"]
    values = [total_mess, total_hostel, total_electricity, total_inventory]

    plt.figure(figsize=(6, 5))
    plt.bar(categories, values, color=["#4CAF50", "#2196F3", "#FF9800", "#F44336"])
    plt.title("Overall Expense Summary (All Students)")
    plt.ylabel("Total Amount (BDT)")
    plt.tight_layout()
    plt.show()

# ------------------- Theme -------------------
def toggle_theme():
    global theme
    if theme["bg"] == "#f0f4f7":
        theme = {"bg": "#2e2e2e", "fg": "white"}
    else:
        theme = {"bg": "#f0f4f7", "fg": "black"}
    apply_theme()

def apply_theme():
    root.configure(bg=theme["bg"])
    for frame in [entry_frame, table_frame, summary_frame, header_frame]:
        frame.configure(bg=theme["bg"])
    for label in entry_frame.winfo_children():
        if isinstance(label, tk.Label):
            label.configure(bg=theme["bg"], fg=theme["fg"])
    for label in summary_frame.winfo_children():
        if isinstance(label, tk.Label):
            label.configure(bg=theme["bg"], fg=theme["fg"])

# ------------------- GUI -------------------
root = tk.Tk()
root.title("Hostel & Mess Management System")
root.state("zoomed")

theme = {"bg": "#f0f4f7", "fg": "black"}
root.configure(bg=theme["bg"])
data = load_data()

header_font = ("Helvetica", 10, "bold")
entry_font = ("Helvetica", 9)

# Header
header_frame = tk.Frame(root, bg=theme["bg"])
header_frame.pack(fill=tk.X, pady=5)
tk.Label(header_frame, text="🏠 Hostel & Mess Management System", font=("Helvetica", 18, "bold"),
         bg=theme["bg"], fg="#1a237e").pack(pady=10)

# Entry Frame
entry_frame = tk.Frame(root, bg=theme["bg"], pady=5)
entry_frame.pack(fill=tk.X, padx=20, pady=10)

tk.Label(entry_frame, text="Roll", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=0, padx=5, pady=2, sticky="w")
def only_numbers(char):
    return char.isdigit()
roll_entry = tk.Entry(entry_frame, font=entry_font, validate="key")
roll_entry['validatecommand'] = (roll_entry.register(only_numbers), '%S')
roll_entry.grid(row=0, column=1, padx=5, pady=2)


tk.Label(entry_frame, text="Student Name", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=2, padx=5, pady=2, sticky="w")
student_name = tk.Entry(entry_frame, font=entry_font)
student_name.grid(row=0, column=3, padx=5, pady=2)

tk.Label(entry_frame, text="Religion", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=4, padx=5, pady=2, sticky="w")
religion_var = tk.StringVar()
religion_menu = ttk.Combobox(entry_frame, textvariable=religion_var, state="readonly",
                             values=["Hindu", "Muslim", "Aboriginal"], font=entry_font)
religion_menu.grid(row=0, column=5, padx=5, pady=2)

tk.Label(entry_frame, text="Prayer Done?", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=6, padx=5, pady=2, sticky="w")
prayer_var = tk.StringVar()
prayer_menu = ttk.Combobox(entry_frame, textvariable=prayer_var, state="readonly",
                           values=["Yes", "No"], font=entry_font)
prayer_menu.grid(row=0, column=7, padx=5, pady=2)

tk.Label(entry_frame, text="Meal Count", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=1, column=0, padx=5, pady=2, sticky="w")
meal_count_entry = tk.Entry(entry_frame, font=entry_font)
meal_count_entry.grid(row=1, column=1, padx=5, pady=2)

tk.Label(entry_frame, text="Meal Expenses", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=1, column=2, padx=5, pady=2, sticky="w")
mess_entry = tk.Entry(entry_frame, font=entry_font)
mess_entry.grid(row=1, column=3, padx=5, pady=2)

tk.Label(entry_frame, text="Hostel Sit Cost (OT)", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=1, column=4, padx=5, pady=2, sticky="w")
hostel_entry = tk.Entry(entry_frame, font=entry_font)
hostel_entry.grid(row=1, column=5, padx=5, pady=2)

tk.Label(entry_frame, text="Electricity (OT)", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=1, column=6, padx=5, pady=2, sticky="w")
electricity_entry = tk.Entry(entry_frame, font=entry_font)
electricity_entry.grid(row=1, column=7, padx=5, pady=2)

tk.Label(entry_frame, text="Inventory (OT)", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=2, column=0, padx=5, pady=2, sticky="w")
inventory_entry = tk.Entry(entry_frame, font=entry_font)
inventory_entry.grid(row=2, column=1, padx=5, pady=2)

tk.Button(entry_frame, text="Add Expense", command=add_expense,
          bg="#4CAF50", fg="white", font=header_font, width=18, pady=5).grid(row=2, column=5, padx=10, pady=5)

tk.Button(entry_frame, text="Show Overall Cost", command=show_overall_chart,
          bg="#FF5722", fg="white", font=header_font, width=20, pady=5).grid(row=2, column=6, padx=10, pady=5)

# Table Frame
table_frame = tk.Frame(root, bg=theme["bg"])
table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

columns = ["Serial", "Roll", "Student", "Date", "Religion", "PrayerDone", "MealCount", "Mess", "Hostel", "Electricity", "Inventory"]
tree = ttk.Treeview(table_frame, columns=columns, show="headings")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", font=("Helvetica", 9), rowheight=25, fieldbackground="#ffffff")
style.configure("Treeview.Heading", font=header_font, background="#ffffff", foreground="black")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor='center', width=100, stretch=True)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
update_table()

# ------------------- Summary Frame -------------------
summary_frame = tk.Frame(root, bg=theme["bg"], pady=10)
summary_frame.pack(fill=tk.X, padx=20, pady=10)

# Labels & Entries (Roll, Date, Month, Year) in one row
tk.Label(summary_frame, text="Enter Roll for Summary:", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=0, padx=5, pady=5, sticky="e")
summary_roll = tk.Entry(summary_frame, font=entry_font)
summary_roll.grid(row=0, column=1, padx=5, pady=5)

tk.Label(summary_frame, text="Date (YYYY-MM-DD):", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=2, padx=5, pady=5, sticky="e")
summary_date = tk.Entry(summary_frame, font=entry_font)
summary_date.grid(row=0, column=3, padx=5, pady=5)

tk.Label(summary_frame, text="Month (1-12):", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=4, padx=5, pady=5, sticky="e")
summary_month = tk.Entry(summary_frame, font=entry_font)
summary_month.grid(row=0, column=5, padx=5, pady=5)

tk.Label(summary_frame, text="Year (YYYY):", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=6, padx=5, pady=5, sticky="e")
summary_year = tk.Entry(summary_frame, font=entry_font)
summary_year.grid(row=0, column=7, padx=5, pady=5)

# Buttons in separate row (original width)
tk.Button(summary_frame, text="Show Summary & Chart", command=show_student_summary,
          bg="#ff9800", fg="white", font=("Helvetica", 11, "bold"), width=20, pady=6).grid(row=1, column=0, padx=5, pady=10, sticky="w")          

tk.Button(summary_frame, text="Change Theme", command=toggle_theme,
          bg="#2196F3", fg="white", font=("Helvetica", 11, "bold"), width=18, pady=6).grid(row=1, column=4, padx=5, pady=10, sticky="e")

# ------------------- New Buttons: Export Month & Clear -------------------
def export_month_data():
    month_filter = summary_month.get().strip()
    year_filter = summary_year.get().strip()

    if not month_filter or not year_filter:
        messagebox.showwarning("Warning", "Please enter Month and Year to export!")
        return

    try:
        month_int = int(month_filter)
        year_int = int(year_filter)
    except ValueError:
        messagebox.showwarning("Warning", "Enter valid Month and Year!")
        return

    export_file = f"export_{year_int}_{month_int}.csv"
    with open(export_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Serial", "Roll", "Student", "Date", "Religion", "PrayerDone",
                         "MealCount", "Mess", "Hostel", "Electricity", "Inventory"])
        for row in data:
            row_date = datetime.strptime(row[3], "%Y-%m-%d")
            if row_date.year == year_int and row_date.month == month_int:
                writer.writerow(row)
    messagebox.showinfo("Success", f"Month data exported to {export_file}")

def clear_all_data():
    global data
    if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
        data = []
        save_data()
        update_table()
        messagebox.showinfo("Info", "All data cleared successfully!")

tk.Button(summary_frame, text="Export Month Data", command=export_month_data,
          bg="#4CAF50", fg="white", font=("Helvetica", 11, "bold"), width=18, pady=6).grid(row=1, column=1, padx=5, pady=10, sticky="w")
          
# Empty column to create space between left and right buttons
tk.Label(summary_frame, text="", bg=theme["bg"]).grid(row=1, column=2, padx=50)

tk.Button(summary_frame, text="Clear All Data", command=clear_all_data,
          bg="#F44336", fg="white", font=("Helvetica", 11, "bold"), width=18, pady=6).grid(row=1, column=3, padx=5, pady=10, sticky="e")

# Run
root.mainloop()
