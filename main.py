import calendar
import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime, timedelta


# The purpose of this program is to provide a GUI that displays user
# inputted key values from a user generated dictionary. These values
# represent upcoming bills as a visual aid and reminder for my elderly
# mother who is the primary user for this application. The bills are
# listed in descending order by due date. Bills change color based on
# how urgently due they are compared to the real life current date.
# Bills will automatically update their due dates based on whether
# they reoccur on the same day every month or reoccur in 30 day cycles
# as long as the bill has been flagged as paid by the user. Paid bills
# are displayed in green until their due date has elapsed. Bills past
# their due dates are displayed in black. One time payment bills are
# not updated and remain until deleted by the user. All bills listed
# remain until deleted. The system will only write or read unless
# prompted by the user.


class BillManager:
    def __init__(self, master):
        self.master = master
        self.master.title("UPCOMING BILLS")

        # Init bill data
        self.bills = []

        # Create main window elements
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack()
        self.main_frame.configure(background="#545454")

        self.bill_listbox = tk.Listbox(self.main_frame, width=40)
        self.bill_listbox.grid(row=0, column=0, columnspan=4, padx=10, pady=5)
        self.bill_listbox.configure(background="#343434",
                                    foreground="#C5C5C5",
                                    font=("Arial", 24))

        self.add_button = tk.Button(self.main_frame, text="ADD", command=self.new_editor)
        self.add_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.add_button.configure(background="#343434",
                                  foreground="#C5C5C5",
                                  font=("Arial", 18))

        self.edit_button = tk.Button(self.main_frame, text="EDIT", command=self.open_editor)
        self.edit_button.grid(row=1, column=1, stick="ew", padx=5, pady=5)
        self.edit_button.configure(background="#343434",
                                   foreground="#C5C5C5",
                                   font=("Arial", 18))

        self.delete_button = tk.Button(self.main_frame, text="DELETE", command=self.delete_bill)
        self.delete_button.grid(row=1, column=2, sticky="ew", padx=5, pady=5)
        self.delete_button.configure(background="#343434",
                                     foreground="#C5C5C5",
                                     font=("Arial", 18))
        self.toggle_paid_button = tk.Button(self.main_frame, text="PAID", command=self.toggle_paid)
        self.toggle_paid_button.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        self.toggle_paid_button.configure(background="#343434",
                                          foreground="#C5C5C5",
                                          font=('Arial', 18))

        # Load bill data from file
        self.load_bills()

    def toggle_paid(self):
        selected_index = self.bill_listbox.curselection()
        if selected_index:  # Check if bill is selected
            selected_bill = self.bills[selected_index[0]]
            selected_bill['paid'] = not selected_bill.get('paid', False)

            # Check if the bill is overdue and update accordingly
            current_date = datetime.now()
            due_day = selected_bill['due_day']
            due_month = selected_bill['due_month']
            check_date = datetime(current_date.year, due_month, due_day)
            if selected_bill['paid'] and check_date < current_date:
                # Update due month
                due_month = (due_month % 12) + 1
                selected_bill['due_month'] = due_month
                selected_bill['paid'] = False

            self.save_bills()  # Add paid boolean to dictionary
            print(selected_bill)
            self.load_bills()  # Reload GUI
        else:
            messagebox.showinfo("Information", "Please select a bill to toggle its paid status.")

    def load_bills(self):
        try:
            # Load bills from file
            with open("bills.json", "r") as file:
                self.bills = json.load(file)
        except FileNotFoundError:
            # If file does not exist init with empty list
            self.bills = []

        # Sort bills by due date
        self.bills.sort(key=lambda x: (x['due_month'], x['due_day']))

        current_date = datetime.now()

        self.bill_listbox.delete(0, tk.END)

        # Load bills into listbox
        for bill in self.bills:
            due_day = bill['due_day']
            due_month = bill['due_month']
            check_date = datetime(current_date.year, due_month, due_day)

            if not bill['paid']:
                # Set unpaid bill color based on closeness of the due date
                difference_in_days = (check_date - current_date).days

                # Assign color based on urgency
                if difference_in_days <= -2:
                    text_color = "black"
                elif 0 >= difference_in_days >= -1:
                    text_color = "red"
                elif 3 >= difference_in_days >= 1:
                    text_color = "orange"
                elif 7 >= difference_in_days >= 4:
                    text_color = "yellow"
                else:
                    text_color = "#C5C5C5"
            else:
                if check_date < current_date:
                    # Update due month to the next month
                    due_month = (due_month % 12) + 1
                    check_date = datetime(current_date.year, due_month, due_day)
                    text_color = "green"
                else:
                    text_color = "green"

            due_date = f"{bill['due_month']:02d}/{bill['due_day']:02d}"
            bill_info = f"{bill['name']}: Due {due_date} - ${bill['amount']}"
            self.bill_listbox.insert(tk.END, bill_info)
            self.bill_listbox.itemconfig(tk.END, {'fg': text_color})

        # Save the updated bills to file
        self.save_bills()

    def open_editor(self):
        selected_index = self.bill_listbox.curselection()
        if selected_index:
            selected_bill = self.bills[selected_index[0]]
            editor = BillEditor(self.master, self, selected_bill)
        else:
            editor = BillEditor(self.master, self)

    def new_editor(self):
        editor = BillEditor(self.master, self)

    def save_bills(self):
        # Save bills to file
        with open("bills.json", "w") as file:
            json.dump(self.bills, file, indent=4)

    def delete_bill(self):
        # Delete selected bill entry
        selected_index = self.bill_listbox.curselection()
        if selected_index:
            # Remove the selected entry
            del self.bills[selected_index[0]]
            # Save updated list
            self.save_bills()
            # Reload bill GUI
            self.load_bills()
        else:
            messagebox.showinfo("Information", "Please select an entry to delete.")


class BillEditor:
    def __init__(self, master, manager, selected_bill=None):
        self.master = master
        self.manager = manager
        self.selected_bill = selected_bill

        # Create editor window
        self.editor_window = tk.Toplevel(master)
        self.editor_window.title("EDIT BILLS")
        self.editor_window.configure(background="#343434")

        # Init entry fields
        self.name_var = tk.StringVar()
        self.due_day_var = tk.IntVar(value=datetime.now().day)  # Default to current day
        self.cycle_type_var = tk.StringVar(value="Every Month")  # Default value
        self.amount_var = tk.DoubleVar(value=0.00)
        self.due_month_var = tk.IntVar(value=datetime.now().month)  # Default to current month
        self.toggle_paid_var = tk.BooleanVar(value=False)  # Default state

        # If selected_bill true populate values
        if selected_bill:
            self.name_var.set(selected_bill['name'])
            self.due_day_var.set(selected_bill['due_day'])
            self.cycle_type_var.set(selected_bill.get('cycle_type', "Every Month"))
            self.amount_var.set(selected_bill['amount'])
            self.due_month_var.set(selected_bill['due_month'])
            self.toggle_paid_var.set(selected_bill['paid'])

        # Entry fields
        tk.Label(self.editor_window, text="Name:",
                 background="#343434",
                 foreground="#C5C5C5",
                 font=('Arial', 14)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.editor_window, textvariable=self.name_var,
                 background="#545454",
                 foreground="#C5C5C5",
                 font=('Arial', 14)).grid(row=0, column=1, columnspan=4, sticky="ew", padx=5, pady=5)
        tk.Label(self.editor_window, text="Due Date:",
                 background="#343434",
                 foreground="#C5C5C5",
                 font=('Arial', 14)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Label(self.editor_window, text="Month:",
                 background="#343434",
                 foreground="#C5C5C5",
                 font=('Arial', 14)).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        spinbox_month = (tk.Spinbox(self.editor_window, from_=1, to=12,
                                    textvariable=self.due_month_var,
                                    background="#545454",
                                    foreground="#C5C5C5",
                                    font=('Arial', 14), width=5))
        spinbox_month.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        spinbox_month.bind("<MouseWheel>", self.on_mouse_wheel)
        tk.Label(self.editor_window, text="Day:",
                 background="#343434",
                 foreground="#C5C5C5",
                 font=('Arial', 14)).grid(row=1, column=3, sticky="w", padx=5, pady=5)
        spinbox_day = tk.Spinbox(self.editor_window, from_=1, to=31,
                                 textvariable=self.due_day_var, width=5,
                                 background="#545454",
                                 foreground="#C5C5C5",
                                 font=('Arial', 14))
        spinbox_day.grid(row=1, column=4, sticky="w", padx=5, pady=5)
        spinbox_day.bind("<MouseWheel>", self.on_mouse_wheel)
        tk.Label(self.editor_window, text="Frequency:",
                 background="#343434",
                 foreground="#C5C5C5",
                 font=('Arial', 14)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.cycle_type_dropdown = tk.OptionMenu(self.editor_window,
                                                 self.cycle_type_var,
                                                 "Every Month",
                                                 "Every 30 Days",
                                                 "One Time Payment")
        self.cycle_type_dropdown.grid(row=2, column=1, columnspan=4, sticky="w", padx=5, pady=5)
        self.cycle_type_dropdown.configure(background="#545454", foreground="#C5C5C5", font=('Arial', 14))
        tk.Label(self.editor_window, text="Amount Due:",
                 background="#343434",
                 foreground="#C5C5C5",
                 font=('Arial', 14)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.editor_window, textvariable=self.amount_var,
                 background="#545454",
                 foreground="#C5C5C5",
                 font=('Arial', 14)).grid(row=3, column=1, columnspan=4, sticky="w", padx=5, pady=5)

        # Buttons
        if selected_bill:
            tk.Button(self.editor_window, text="UPDATE",
                      background="#343434",
                      foreground="#C5C5C5",
                      font=('Arial', 14),
                      command=self.update_bill).grid(row=4, column=0, columnspan=2, sticky="e", pady=5)
        else:
            tk.Button(self.editor_window, text="SAVE",
                      background="#343434",
                      foreground="#C5C5C5",
                      font=('Arial', 14),
                      command=self.save_bill).grid(row=4, column=0, columnspan=2, sticky="e", pady=5)
        tk.Button(self.editor_window, text="CANCEL",
                  background="#343434",
                  foreground="#C5C5C5",
                  font=('Arial', 14),
                  command=self.editor_window.destroy).grid(row=4, column=2, columnspan=2, sticky="w", pady=5)

    def on_mouse_wheel(self, event):
        widget = event.widget
        delta = -1 if event.delta < 0 else 1
        widget.invoke("buttondown" if delta > 0 else "buttonup")

    def save_bill(self):
        name = self.name_var.get()
        due_day = self.due_day_var.get()
        cycle_type = self.cycle_type_var.get()
        amount = self.amount_var.get()
        due_month = self.due_month_var.get()
        toggle_paid = self.toggle_paid_var.get()

        current_date = datetime.now()
        max_days_in_month = calendar.monthrange(current_date.year, due_month)[1]

        if toggle_paid:
            due_month = current_date.month if current_date.day <= due_day else current_date.month + 1

        if 1 <= due_day <= max_days_in_month:
            due_date = f"{due_month:02d}/{due_day:02d}"  # Format as MM/DD

            self.manager.bills.append({'name': name,
                                       'due_day': due_day,
                                       'due_month': due_month,
                                       'cycle_type': cycle_type,
                                       'amount': amount,
                                       'paid': toggle_paid})
            self.manager.save_bills()  # Save bills to file
            self.manager.load_bills()  # Reload bills in GUI
            self.editor_window.destroy()

        else:
            messagebox.showerror("Error", "Invalid due day")

    def update_bill(self):
        name = self.name_var.get()
        due_day = self.due_day_var.get()
        cycle_type = self.cycle_type_var.get()
        amount = self.amount_var.get()
        due_month = self.due_month_var.get()

        # Always set 'paid' status to false when updating a bill
        toggle_paid = False

        current_date = datetime.now()
        max_days_in_month = calendar.monthrange(current_date.year, due_month)[1]

        if 1 <= due_day <= max_days_in_month:
            due_date = f"{due_month:02d}/{due_day:02d}"  # Format as MM/DD

            for bill in self.manager.bills:
                if bill['name'] == self.selected_bill['name']:
                    bill.update({'name': name,
                                 'due_day': due_day,
                                 'due_month': due_month,
                                 'cycle_type': cycle_type,
                                 'amount': amount,
                                 'paid': toggle_paid})  # Set 'paid' to False
                    break

            self.manager.save_bills()  # Save bills to file
            self.manager.load_bills()  # Reload bills in GUI
            self.editor_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid due day")

    def delete_bill(self):
        if self.selected_bill:
            self.manager.bills.remove(self.selected_bill)
            self.manager.save_bills()  # Save bills to file
            self.manager.load_bills()  # Reload bills in GUI
            self.editor_window.destroy()


def main():
    root = tk.Tk()
    app = BillManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
