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

# ------------------- Add Expense -------------------
def add_expense():
    global edit_index
    roll = roll_entry.get().strip()
    student = student_name.get().strip()
    religion = religion_var.get()
    prayer_done = prayer_var.get()
    meal_count = meal_count_entry.get().strip()
    meal_count_str = meal_count_entry.get().strip()
    try:
        meal_count = int(meal_count_str or 1)
    except ValueError:
        messagebox.showwarning("Warning", "Enter a valid number for meal count!")
        return

    if meal_count > 10:
        response = messagebox.askyesno(
            "High Meal Count",
            f"Meal count is {meal_count}, which is unusually high.\nDo you want to proceed?"
        )
        if not response:
            return

    if not roll or not student or not religion or not prayer_done:
        messagebox.showwarning("Warning", "All required fields must be filled!")
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
        meal_count += 1
    mess *= meal_count

    if edit_index is not None:
        data[edit_index] = [
            edit_index + 1, roll, student, datetime.now().strftime("%Y-%m-%d"),
            religion, prayer_done, meal_count, mess, hostel, electricity, inventory
        ]
        edit_index = None
        add_button.config(text="Add Expense")
        messagebox.showinfo("Success", "Record updated successfully!")
    else:
        serial = len(data) + 1
        data.append([
            serial, roll, student, datetime.now().strftime("%Y-%m-%d"),
            religion, prayer_done, meal_count, mess, hostel, electricity, inventory
        ])
        messagebox.showinfo("Success", "New expense added!")

    save_data()
    update_table()

    # Clear all entries
    roll_entry.delete(0, tk.END)
    student_name.delete(0, tk.END)
    religion_var.set('')
    prayer_var.set('')
    meal_count_entry.delete(0, tk.END)
    mess_entry.delete(0, tk.END)
    # hostel_entry.delete(0, tk.END)
    # electricity_entry.delete(0, tk.END)
    # inventory_entry.delete(0, tk.END)
    total_students_var.set(f"Total Students: {len(data)}")
    total_cost_var.set(f"Total Cost Today: {sum([float(row[7])+float(row[8])+float(row[9])+float(row[10]) for row in data]):.2f}৳")

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

def show_notice():
    notice_win = tk.Toplevel(root)
    notice_win.title("Notice Board")
    notice_win.geometry("550x350")
    notice_win.config(bg="#f0f4f8")

    # Heading
    tk.Label(
        notice_win, text="📢 Hostel & Mess Notices", 
        font=("Helvetica", 16, "bold"), fg="#1a73e8", bg="#f0f4f8"
    ).pack(pady=15)

    # Notice body
    notice_text = (
        "Dear Students,\n\n"
        "1. Maintenance will be carried out in the hostel on 25th of this month.\n"
        "2. Mess menu has been updated for this week.\n"
        "3. Submit your daily meal count before 10 PM to avoid penalties.\n"
        "4. For any hostel-related issues, contact the admin immediately.\n\n"
        "Stay safe and take care of your belongings!\n\n"
        "— Hostel Management Team"
    )
    tk.Label(
        notice_win, text=notice_text, 
        font=("Helvetica", 12), justify="left", bg="#f0f4f8"
    ).pack(padx=20, pady=10, anchor="w")


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
    if theme["bg"] == "#2e2e2e":
        header_frame.configure(bg="black")
    else:
        header_frame.configure(bg="#cce5ff")
    
    for frame in [entry_frame, table_frame, summary_frame]:
        frame.configure(bg=theme["bg"])

    for label in entry_frame.winfo_children():
        if isinstance(label, tk.Label):
            label.configure(bg=theme["bg"], fg=theme["fg"])
    for label in summary_frame.winfo_children():
        if isinstance(label, tk.Label):
            label.configure(bg=theme["bg"], fg=theme["fg"])
            
# ------------------- Feedback Functions -------------------
def show_feedback_popup():
    popup = tk.Toplevel(root)
    popup.title("Give Feedback")
    popup.geometry("400x250")
    popup.configure(bg=theme["bg"])

    tk.Label(popup, text="Your Feedback:", font=("Helvetica",12,"bold"),
             bg=theme["bg"], fg=theme["fg"]).pack(pady=10)

    feedback_entry = tk.Text(popup, height=8, width=50, font=("Helvetica",10))
    feedback_entry.pack(pady=5)

    def submit_feedback():
        feedback = feedback_entry.get("1.0", tk.END).strip()
        if feedback:
            with open("feedback.csv", "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), feedback])
            popup.destroy()
            show_toast("Feedback submitted. Thank you!")
        else:
            messagebox.showwarning("Warning", "Please write something!")

    tk.Button(popup, text="Submit", command=submit_feedback,
              bg="#4CAF50", fg="white", font=("Helvetica",11,"bold")).pack(pady=10)

def show_toast(msg, duration=2000):
    toast = tk.Label(root, text=msg, bg="#333", fg="white", font=("Helvetica",10), bd=1, relief="solid")
    toast.place(relx=0.5, rely=0.05, anchor="n")
    root.after(duration, lambda: toast.destroy())

# ------------------- GUI -------------------
import tkinter as tk
import time

# ---------- Splash Screen ----------
splash = tk.Tk()
splash.overrideredirect(True)
splash.geometry("500x280+450+200")
splash.configure(bg="#1E1E2F")

# Gradient-style effect using two frames
top_color = "#2C2C54"
bottom_color = "#1E1E2F"
canvas = tk.Canvas(splash, width=500, height=280, highlightthickness=0)
canvas.pack(fill="both", expand=True)

for i in range(0, 280):
    color = f"#{int(30 + (i/280)*20):02x}{int(30 + (i/280)*20):02x}{int(47 + (i/280)*40):02x}"
    canvas.create_line(0, i, 500, i, fill=color)

# Title text
title = tk.Label(splash, text="🏠 Hostel & Mess Management System",
                 font=("Segoe UI", 18, "bold"),
                 fg="#FFD700", bg="#2C2C54")
title.place(relx=0.5, rely=0.35, anchor="center")

text = "Please wait, running your Hostel Management System..."
for offset, color in [(-1, "#111"), (1, "#111"), (0, "#F4FBFA")]:
    tk.Label(splash, text=text,
             font=("Calibri", 14, "italic"),
             fg=color, bg="#1E1E2F").place(relx=0.5 + offset*0.001, rely=0.55 + offset*0.001, anchor="center")

# Loading text
loading_label = tk.Label(splash, text="Loading...",
                         font=("Calibri", 12, "bold"),
                         fg="#00FFAA", bg="#1E1E2F")
loading_label.place(relx=0.5, rely=0.68, anchor="center")

# Progress bar (animated block style)
progress = tk.Label(splash, text="", font=("Consolas", 12),
                    fg="#00FF00", bg="#1E1E2F")
progress.place(relx=0.5, rely=0.8, anchor="center")

def animate_progress():
    for i in range(1, 21):
        progress.config(text="█" * i)
        splash.update()
        time.sleep(0.09)
    splash.destroy()

splash.after(700, animate_progress)
splash.mainloop()

# ---------- Main Window ----------
root = tk.Tk()
root.title("Hostel & Mess Management System")
root.geometry("800x600")
root.configure(bg="white")

def daily_reminder():
    messagebox.showinfo("Reminder", "Remember to submit today’s meal count before 10 PM!")
root.after(1000, daily_reminder)

root.title("Hostel & Mess Management System")
root.state("zoomed")

theme = {"bg": "#f0f4f7", "fg": "black"}
root.configure(bg=theme["bg"])
data = load_data()

header_font = ("Helvetica", 10, "bold")
entry_font = ("Helvetica", 9)

def show_exit_splash():
    exit_splash = tk.Toplevel()
    exit_splash.overrideredirect(True)
    exit_splash.geometry("500x250+450+200")
    exit_splash.configure(bg="#121212")

    main_text = "✨ Thank you for using Hostel & Mess Management System"
    for offset, color in [(-1, "#003333"), (1, "#003333"), (0, "#00FFAA")]:
        tk.Label(exit_splash, text=main_text,
                 font=("Segoe UI", 12, "bold"),
                 fg=color, bg="#121212").place(relx=0.5 + offset*0.002,
                                                 rely=0.4 + offset*0.002,
                                                 anchor="center")
    def pulse(label, alpha=0):
        alpha += 0.05
        if alpha > 1:
            alpha = 0
        label.configure(fg=f"#{int(204*alpha):02x}{int(204*alpha):02x}{int(204*alpha):02x}")
        exit_splash.after(100, lambda: pulse(label, alpha))

    sub_label = tk.Label(exit_splash, text="See you next time, happy managing!",
                        font=("Calibri", 14, "italic"),
                        fg="#CCCCCC", bg="#121212")
    sub_label.place(relx=0.5, rely=0.6, anchor="center")
    pulse(sub_label)

    def fade(alpha=100):
        if alpha >= 0:
            exit_splash.attributes("-alpha", alpha/100)
            exit_splash.after(50, lambda: fade(alpha-5))
        else:
            exit_splash.destroy()
            root.quit()

    exit_splash.after(2000, fade)

root.protocol("WM_DELETE_WINDOW", lambda: [root.withdraw(), show_exit_splash()])

# Header
header_frame = tk.Frame(root, bg="#cce5ff", pady=10)
header_frame.pack(fill=tk.X, pady=5)

tk.Label(header_frame, text="🏠 Hostel & Mess Management System",
         font=("Helvetica", 16, "bold"),
         bg="#cce5ff", fg="#1a237e").pack(side=tk.LEFT, padx=16)

# ------------------- Help Button -------------------
def show_help():
    popup = tk.Toplevel(root)
    popup.title("Help")
    popup.configure(bg="#f0f4f7")
    popup.geometry("580x480")

    tk.Label(popup, 
        text="🏠 Hostel & Mess Management System - Help Center",
        font=("Helvetica", 16, "bold"),
        fg="#1a237e",
        bg="#f0f4f7",
        justify="center",
        anchor="n"
    ).pack(fill=tk.X, pady=(10,15))
    tk.Label(popup, text=(
        "Instructions for Students:\n\n"
        "1. Fill in your Roll Number and Full Name.\n"
        "2. Select your Religion and indicate if Prayer was done.\n"
        "3. Enter the number of meals taken.\n"
        "4. Provide numeric values for Mess, Hostel, Electricity, and Inventory costs.\n"
        "5. Click 'Add Expense' to save your daily records.\n"
        "6. Use 'Show Overall Cost' to view the total expenses for all students.\n"
        "7. Use the 'Summary' section to view student-wise expense breakdown and charts.\n"
    ),
        font=("Helvetica", 12),
        bg="#f0f4f7", fg="black",
        justify="left",
        wraplength=480
    ).pack(padx=10, pady=10)
    
    tk.Label(popup, text="⚠️ Note: If 'Prayer Done' is marked 'No', an extra meal penalty is automatically applied.",
         font=("Helvetica", 12, "bold"),
         bg="#f0f4f7", fg="red",
         justify="left",
         wraplength=480
    ).pack(padx=10, pady=(0,10),anchor="n")
    
    # ---------------- Version Info Section ----------------
    tk.Label(
    popup,
    text="System Version: 1.0 || Developed by BugBusters Team\nContact: 01887538750",
    font=("Helvetica", 11, "bold italic"),
    fg="#2c3e50",
    bg="#f0f4f7",
    justify="center"
    ).pack(pady=(20, 8))
    
    tk.Button(popup, text="Close", command=popup.destroy,
              font=("Helvetica", 12, "bold"),
              padx=10, pady=3,
              bg="#ff9800", fg="white").pack(pady=10)

# ------------------- Header Help Button -------------------
tk.Button(header_frame, text="Help", command=show_help,
          bg="#286CB9", fg="white",
          font=("Helvetica", 12, "bold"),
          padx=10, pady=3).pack(side=tk.RIGHT, padx=10)

tk.Button(header_frame, text="Change Theme", command=toggle_theme,
          bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"),padx=10, pady=3).pack(side=tk.RIGHT, padx=10)

# ------------------- Add Feedback Button in Header -------------------
tk.Button(header_frame, text="Feedback", command=show_feedback_popup,
          bg="#FF5722", fg="white", font=("Helvetica", 12, "bold"), padx=10, pady=3).pack(side=tk.RIGHT, padx=10)

info_frame = tk.Frame(root, bg=theme["bg"])
info_frame.pack(fill=tk.X, padx=20, pady=5)

total_students_var = tk.StringVar(value=f"Total Students: {len(data)}")
total_cost_var = tk.StringVar(value=f"Total Cost Today: {sum([float(row[7])+float(row[8])+float(row[9])+float(row[10]) for row in data]):.2f}৳")

tk.Label(info_frame, textvariable=total_students_var, font=("Helvetica",12,"bold"), bg="#4CAF50", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=5)
tk.Label(info_frame, textvariable=total_cost_var, font=("Helvetica",12,"bold"), bg="#2196F3", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=5)

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

global add_button
add_button = tk.Button(entry_frame, text="Add Expense", command=add_expense,
                       bg="#4CAF50", fg="white", font=header_font, width=18, pady=5)
add_button.grid(row=2, column=5, padx=10, pady=5)

tk.Button(entry_frame, text="Show Overall Cost", command=show_overall_chart,
          bg="#FF5722", fg="white", font=header_font, width=20, pady=5).grid(row=2, column=6, padx=10, pady=5)

edit_index = None  # global variable to track edited row

def edit_record():
    global edit_index
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a row first!")
        return
    edit_index = tree.index(selected[0])  # Get index of selected row in Treeview
    item = data[edit_index]

    # Populate entries with selected row
    roll_entry.delete(0, tk.END)
    roll_entry.insert(0, item[1])
    student_name.delete(0, tk.END)
    student_name.insert(0, item[2])
    religion_var.set(item[4])
    prayer_var.set(item[5])
    meal_count_entry.delete(0, tk.END)
    meal_count_entry.insert(0, item[6])
    mess_entry.delete(0, tk.END)
    mess_entry.insert(0, item[7])
    hostel_entry.delete(0, tk.END)
    hostel_entry.insert(0, item[8])
    electricity_entry.delete(0, tk.END)
    electricity_entry.insert(0, item[9])
    inventory_entry.delete(0, tk.END)
    inventory_entry.insert(0, item[10])

    add_button.config(text="Save Changes")  # change button text

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a row first!")
        return
    item_index = tree.index(selected[0])  # Use index instead of item value
    item = data[item_index]
    if messagebox.askyesno("Confirm Delete", f"Delete record for Roll {item[1]}?"):
        data.pop(item_index)  # remove by index
        save_data()
        update_table()
        messagebox.showinfo("Info", "Record deleted successfully!")

# ------------------- Right-Click Menu -------------------
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Edit", command=edit_record)
menu.add_command(label="Delete", command=delete_record)

def popup_menu(event):
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

# Table Frame
table_frame = tk.Frame(root, bg=theme["bg"])
table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

columns = ["Serial", "Roll", "Student", "Date", "Religion", "PrayerDone", "MealCount", "Mess", "Hostel", "Electricity", "Inventory"]
tree = ttk.Treeview(table_frame, columns=columns, show="headings")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
                font=("Helvetica", 9),
                rowheight=25,
                fieldbackground="white")
style.configure("Treeview.Heading",
                font=header_font,
                background="#ffffff",
                foreground="black")

tree.tag_configure('oddrow', background='#e0e0e0')
tree.tag_configure('evenrow', background='#ffffff')

def update_table():
    for row in tree.get_children():
        tree.delete(row)
    for i, row in enumerate(data):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert("", tk.END, values=row, tags=(tag,))

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor='center', width=100, stretch=True)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.bind("<Button-3>", popup_menu)
update_table()

# ------------------- Summary Frame -------------------
summary_frame = tk.Frame(root, bg=theme["bg"], pady=10)
summary_frame.pack(fill=tk.X, padx=20, pady=10)

for i in range(8):  # 0 to 7 columns
    summary_frame.columnconfigure(i, weight=1)

# Labels and Entries
tk.Label(summary_frame, text="Enter Roll for Summary:", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=0, padx=5, pady=5, sticky="e")
summary_roll = tk.Entry(summary_frame, font=entry_font)
summary_roll.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

tk.Label(summary_frame, text="Date (YYYY-MM-DD):", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=2, padx=5, pady=5, sticky="e")
summary_date = tk.Entry(summary_frame, font=entry_font)
summary_date.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

tk.Label(summary_frame, text="Month (1-12):", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=4, padx=5, pady=5, sticky="e")
summary_month = tk.Entry(summary_frame, font=entry_font)
summary_month.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

tk.Label(summary_frame, text="Year (YYYY):", font=header_font, bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=6, padx=5, pady=5, sticky="e")
summary_year = tk.Entry(summary_frame, font=entry_font)
summary_year.grid(row=0, column=7, padx=5, pady=5, sticky="ew")

# Buttons in separate row (original width)
tk.Button(summary_frame, text="Show Summary & Chart", command=show_student_summary,
          bg="#ff9800", fg="white", font=("Helvetica", 11, "bold"), width=20, pady=6).grid(row=1, column=0, padx=5, pady=10, sticky="w")          

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

# Notice Board button next to Clear All Data
notice_button = tk.Button(summary_frame, text="Notice Board",
                          command=lambda: show_notice(),
                          bg="#F44336", fg="white", font=("Helvetica", 11, "bold"), width=18, pady=6)
notice_button.grid(row=1, column=4, padx=5, pady=10, sticky="w")

# Run
root.mainloop()
