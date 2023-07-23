import tkinter as tk
from tkinter import messagebox
import sqlite3
import time

# Database connection
conn = sqlite3.connect("time_tracker.db")
cursor = conn.cursor()

# Create the table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS time_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT,
        start_time REAL,
        end_time REAL,
        total_time REAL
    )
""")
conn.commit()

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker App")
        self.root.geometry("400x300")
        self.root.config(bg="#2c3e50")  # Dark mode background color

        self.game_name_label = tk.Label(root, text="Game Name:", bg="#2c3e50", fg="white")
        self.game_name_label.grid(row=0, column=0, padx=10, pady=5)

        self.game_name_entry = tk.Entry(root)
        self.game_name_entry.grid(row=0, column=1, padx=10, pady=5)

        self.start_stop_button = tk.Button(root, text="Start/Stop Tracking", command=self.start_stop_tracking, bg="#16a085", fg="white")
        self.start_stop_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.reset_button = tk.Button(root, text="Reset Timer", command=self.reset, bg="#c0392b", fg="white")
        self.reset_button.grid(row=1, column=2, padx=10, pady=5)

        self.delete_button = tk.Button(root, text="Delete Record", command=self.delete_record, bg="#e74c3c", fg="white")
        self.delete_button.grid(row=1, column=3, padx=10, pady=5)

        self.elapsed_time_label = tk.Label(root, text="Elapsed Time: 0 hours, 0 minutes, 0 seconds", font=("Arial", 14), bg="#2c3e50", fg="white")
        self.elapsed_time_label.grid(row=2, column=0, columnspan=4, padx=10, pady=5)

        self.record_listbox = tk.Listbox(root, width=60, bg="#34495e", fg="white", selectbackground="#2980b9")
        self.record_listbox.grid(row=3, column=0, columnspan=4, padx=10, pady=5)

        self.show_records()

        self.game_name = ""
        self.start_time = None
        self.tracking = False
        self.total_time_played = 0
        self.selected_record = None
        self.update_time()

    def start_stop_tracking(self):
        if self.tracking:
            self.stop_tracking()
        else:
            self.start_tracking()

    def start_tracking(self):
        if self.tracking:
            messagebox.showinfo("Warning", "Tracking is already in progress.")
        else:
            self.game_name = self.game_name_entry.get().strip()
            if not self.game_name:
                messagebox.showerror("Error", "Please enter a game name.")
                return

            if self.selected_record:
                # If a record is selected, add the time on top of it
                selected_id, _, _, _, _ = self.selected_record
                self.total_time_played = cursor.execute("SELECT total_time FROM time_tracking WHERE id = ?", (selected_id,)).fetchone()[0]

            self.start_time = time.time()
            self.tracking = True
            self.start_stop_button.config(text="Stop Tracking", bg="#e74c3c")
            self.update_time()

    def stop_tracking(self):
        if not self.tracking:
            messagebox.showinfo("Warning", "Tracking is not in progress.")
        else:
            end_time = time.time()
            elapsed_seconds = int(end_time - self.start_time)
            self.total_time_played += elapsed_seconds
            self.tracking = False
            self.start_stop_button.config(text="Start Tracking", bg="#16a085")
            self.insert_record()
            self.show_records()

    def insert_record(self):
        if self.selected_record:
            # If a record is selected, update the time
            selected_id, _, _, _, _ = self.selected_record
            cursor.execute("UPDATE time_tracking SET total_time = ? WHERE id = ?", (self.total_time_played, selected_id))
        else:
            # Insert a new record
            cursor.execute("""
                INSERT INTO time_tracking (game_name, start_time, end_time, total_time)
                VALUES (?, ?, ?, ?)
            """, (self.game_name, self.start_time, time.time(), self.total_time_played))
        conn.commit()

    def delete_record(self):
        if self.selected_record:
            selected_id, game_name, _, _, _ = self.selected_record
            response = messagebox.askyesno("Confirmation", f"Are you sure you want to delete the record for {game_name}?")
            if response == tk.YES:
                cursor.execute("DELETE FROM time_tracking WHERE id = ?", (selected_id,))
                conn.commit()
                self.reset()
                self.show_records()

    def show_records(self):
        self.record_listbox.delete(0, tk.END)

        cursor.execute("SELECT * FROM time_tracking ORDER BY id DESC")
        records = cursor.fetchall()

        for record in records:
            game_name = record[1]
            start_time = record[2]
            end_time = record[3]
            total_time = record[4]
            self.record_listbox.insert(tk.END, f"Game: {game_name} - Start: {start_time} - End: {end_time} - Total Time: {self.format_time(total_time)}")

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours} hours, {minutes} minutes, {seconds} seconds"

    def reset(self):
        self.game_name_entry.delete(0, tk.END)
        self.game_name = ""
        self.start_time = None
        self.tracking = False
        self.total_time_played = 0
        self.selected_record = None
        self.start_stop_button.config(text="Start Tracking", bg="#16a085")
        self.elapsed_time_label.config(text="Elapsed Time: 0 hours, 0 minutes, 0 seconds")

    def update_time(self):
        if self.tracking:
            current_time = time.time()
            elapsed_seconds = int(current_time - self.start_time + self.total_time_played)
            self.elapsed_time_label.config(text=f"Elapsed Time: {self.format_time(elapsed_seconds)}")
        self.root.after(1000, self.update_time)  # Update time every 1 second

    def on_record_select(self, event):
        selected_index = self.record_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            selected_record = self.record_listbox.get(selected_index)
            selected_id = selected_record.split()[2]  # Get the ID from the selected record
            self.selected_record = cursor.execute("SELECT * FROM time_tracking WHERE id = ?", (selected_id,)).fetchone()
            self.reset()
            self.start_stop_tracking()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()

# Close the database connection
conn.close()
