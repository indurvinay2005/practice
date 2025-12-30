import tkinter as tk
from tkinter import messagebox
import threading

try:
    from playsound import playsound
except ImportError:
    def playsound(path): pass

# Constants
WORK_TIME = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 15 * 60
ALARM_SOUND = "C:\\Users\\INDURBABU\\Music\\Deva Deva.mp3"

PRIMARY_BG = "#22223b"
TIMER_BG = "#4a4e69"
BTN_START = "#38b000"
BTN_PAUSE = "#f9c74f"
BTN_RESET = "#f94144"
TIMER_FG = "#f2e9e4"
STATUS_FG = "#9a8c98"

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("370x350")
        self.root.resizable(False, False)
        self.root.configure(bg=PRIMARY_BG)

        self.time_left = WORK_TIME
        self.running = False
        self.is_work = True

        # Timer display
        self.timer_frame = tk.Frame(root, bg=TIMER_BG, bd=0, relief="flat")
        self.timer_frame.place(relx=0.5, rely=0.23, anchor="center", relwidth=0.85, relheight=0.32)
        self.timer_label = tk.Label(
            self.timer_frame, text=self.format_time(self.time_left),
            font=("Courier New", 48, "bold"), fg=TIMER_FG, bg=TIMER_BG
        )
        self.timer_label.pack(expand=True, fill="both")

        # Status
        self.status_label = tk.Label(
            root, text="Ready", font=("Arial", 14, "bold"),
            fg=STATUS_FG, bg=PRIMARY_BG
        )
        self.status_label.place(relx=0.5, rely=0.52, anchor="center")

        # Custom time setter
        self.custom_frame = tk.Frame(root, bg=PRIMARY_BG)
        self.custom_frame.place(relx=0.5, rely=0.62, anchor="center")
        self.custom_entry = tk.Entry(self.custom_frame, width=7, font=("Arial", 13), justify='center', bd=1, relief="solid")
        self.custom_entry.grid(row=0, column=0, padx=(0, 5))
        self.set_custom_btn = tk.Button(
            self.custom_frame, text="⏱", command=self.set_custom_time,
            width=3, font=("Arial", 12, "bold"), bg="#3a86ff", fg="white", bd=0, activebackground="#4361ee"
        )
        self.set_custom_btn.grid(row=0, column=1)

        # Buttons
        self.btn_frame = tk.Frame(root, bg=PRIMARY_BG)
        self.btn_frame.place(relx=0.5, rely=0.78, anchor="center")

        self.start_btn = tk.Button(
            self.btn_frame, text="▶", command=self.start_timer,
            width=5, height=2, font=("Arial", 14, "bold"),
            bg=BTN_START, fg="white", bd=0, activebackground="#70e000", cursor="hand2"
        )
        self.start_btn.grid(row=0, column=0, padx=8)

        self.pause_btn = tk.Button(
            self.btn_frame, text="⏸", command=self.pause_timer,
            width=5, height=2, font=("Arial", 14, "bold"),
            bg=BTN_PAUSE, fg="white", bd=0, activebackground="#f9844a", cursor="hand2"
        )
        self.pause_btn.grid(row=0, column=1, padx=8)

        self.reset_btn = tk.Button(
            self.btn_frame, text="⟲", command=self.reset_timer,
            width=5, height=2, font=("Arial", 14, "bold"),
            bg=BTN_RESET, fg="white", bd=0, activebackground="#f3722c", cursor="hand2"
        )
        self.reset_btn.grid(row=0, column=2, padx=8)

        # Sound notification checkbox
        self.sound_var = tk.IntVar(value=1)
        self.sound_check = tk.Checkbutton(
            root, text="🔔", variable=self.sound_var, bg=PRIMARY_BG, fg="#fff",
            selectcolor=PRIMARY_BG, activebackground=PRIMARY_BG, font=("Arial", 13, "bold"),
            bd=0, highlightthickness=0
        )
        self.sound_check.place(relx=0.93, rely=0.05, anchor="ne")

    def format_time(self, secs):
        mins, secs = divmod(secs, 60)
        hrs, mins = divmod(mins, 60)
        if hrs > 0:
            return f"{hrs:02}:{mins:02}:{secs:02}"
        else:
            return f"{mins:02}:{secs:02}"

    def set_custom_time(self):
        value = self.custom_entry.get().strip()
        try:
            if ':' in value:
                parts = value.split(':')
                if len(parts) == 2:
                    mins, secs = map(int, parts)
                    total = mins * 60 + secs
                elif len(parts) == 3:
                    hrs, mins, secs = map(int, parts)
                    total = hrs * 3600 + mins * 60 + secs
                else:
                    raise ValueError
            else:
                total = int(value) * 60
            if total <= 0:
                raise ValueError
            self.time_left = total
            self.is_work = True
            self.timer_label.config(text=self.format_time(self.time_left))
            self.status_label.config(text="Custom timer set!", fg="#3a86ff")
        except Exception:
            messagebox.showerror("Invalid Input", "Enter time as mm:ss or hh:mm:ss or just minutes.")

    def start_timer(self):
        if not self.running and self.time_left > 0:
            self.running = True
            self.status_label.config(
                text="Working..." if self.is_work else "Break!",
                fg=BTN_START if self.is_work else BTN_PAUSE
            )
            self.update_timer()

    def update_timer(self):
        if self.running and self.time_left > 0:
            self.timer_label.config(text=self.format_time(self.time_left))
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0 and self.running:
            self.running = False
            self.timer_label.config(text=self.format_time(0))
            if self.sound_var.get():
                self.play_sound()
            if self.is_work:
                self.status_label.config(text="Break time!", fg=BTN_PAUSE)
                self.time_left = SHORT_BREAK
            else:
                self.status_label.config(text="Back to work!", fg=BTN_START)
                self.time_left = WORK_TIME
            self.is_work = not self.is_work
            self.start_timer()

    def pause_timer(self):
        self.running = False
        self.status_label.config(text="Paused", fg=BTN_PAUSE)

    def reset_timer(self):
        self.running = False
        self.time_left = WORK_TIME
        self.is_work = True
        self.timer_label.config(text=self.format_time(self.time_left))
        self.status_label.config(text="Ready", fg=STATUS_FG)

    def play_sound(self):
        threading.Thread(target=lambda: playsound(ALARM_SOUND), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
