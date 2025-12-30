import tkinter as tk
from tkinter import messagebox

class StudyTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Timer")
        self.root.geometry("350x250")
        self.root.resizable(False, False)

        self.time_left = 0
        self.running = False

        # Entry for input
        self.label = tk.Label(root, text="Enter Time (HH:MM:SS)", font=("Arial", 12))
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, font=("Arial", 16), justify='center')
        self.entry.pack(pady=5)

        # Timer display
        self.timer_label = tk.Label(root, text="00:00:00", font=("Courier", 36), fg="green")
        self.timer_label.pack(pady=20)

        # Buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.start_btn = tk.Button(self.button_frame, text="Start", command=self.start_timer, width=8)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(self.button_frame, text="Pause", command=self.pause_timer, width=8)
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(self.button_frame, text="Reset", command=self.reset_timer, width=8)
        self.reset_btn.grid(row=0, column=2, padx=5)

    def start_timer(self):
        if not self.running:
            input_time = self.entry.get()
            try:
                h, m, s = map(int, input_time.strip().split(":"))
                self.time_left = h * 3600 + m * 60 + s
                if self.time_left <= 0:
                    raise ValueError
                self.running = True
                self.update_timer()
            except Exception:
                messagebox.showerror("Invalid Input", "Please enter time in HH:MM:SS format and make sure it's positive.")

    def update_timer(self):
        if self.running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            hours, mins = divmod(mins, 60)
            time_format = f"{hours:02d}:{mins:02d}:{secs:02d}"
            self.timer_label.config(text=time_format)
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0 and self.running:
            self.timer_label.config(text="00:00:00")
            self.running = False
            messagebox.showinfo("Time's up!", "Your study session is over!")

    def pause_timer(self):
        self.running = False

    def reset_timer(self):
        self.running = False
        self.time_left = 0
        self.timer_label.config(text="00:00:00")
        self.entry.delete(0, tk.END)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimer(root)
    root.mainloop()
