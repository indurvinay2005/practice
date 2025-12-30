"""
Hangman — Pro (all-in-one single-file)

Features:
- GUI (Tkinter) + Console mode
- Word list from file (words.txt) with category support, plus built-in fallback categories
- Difficulty levels + custom lives
- Hints (reveal one letter) with score penalty
- Scoring system based on word length, difficulty, lives remaining
- Persistent high-score leaderboard saved to hangman_scores.json
- Save & resume game state (hangman_save.json)
- Two-player mode (player 1 enters secret word)
- Keyboard support in GUI and quick UX improvements
- Cross-platform sound: winsound on Windows, tkinter bell fallback
- Clean code structure and helpful comments for beginners

Usage:
- Run GUI (default):
    python hangman_pro.py
- Run console mode:
    python hangman_pro.py --console
- Use alternate words file:
    python hangman_pro.py --words=mywords.txt

Create a words file (optional) with optional category tags:
- Format: category:word
  Example:
    animals:elephant
    tech:python
  If no colon, words go into 'default' category.
"""

import random
import string
import json
import os
import sys
import argparse
import time

# Try importing tkinter; if not available, GUI won't run.
try:
    import tkinter as tk
    from tkinter import ttk, simpledialog, messagebox
except Exception:
    tk = None

# winsound for beep on Windows; otherwise fallback to tk bell or no-sound
try:
    import winsound
except Exception:
    winsound = None

# ----------------------------- Configuration -----------------------------

DEFAULT_WORDS_FILE = "words.txt"
SCORES_FILE = "hangman_scores.json"
SAVE_FILE = "hangman_save.json"

# Built-in categories and words fallback (small list)
BUILTIN_CATEGORIES = {
    "tech": ["python", "algorithm", "database", "variable", "function", "developer", "internet"],
    "animals": ["elephant", "tiger", "giraffe", "kangaroo", "dolphin", "penguin"],
    "common": ["hangman", "program", "keyboard", "network", "science", "education"],
}

# Difficulty presets: name -> (lives, score_multiplier)
DIFFICULTY = {
    "Easy": (8, 0.8),
    "Normal": (6, 1.0),
    "Hard": (4, 1.4),
}

# Maximum wrong stages that our GUI drawing supports nicely (used also for console ASCII)
MAX_STAGES = 8

# ----------------------------- Utilities -----------------------------

def play_beep():
    """Cross-platform beep: tries winsound, else Tk bell if available."""
    try:
        if winsound:
            winsound.Beep(750, 120)  # freq, duration
        elif tk:
            # create a temporary root to ring bell if none exists
            try:
                tk._default_root.bell()
            except Exception:
                # fallback: print bell char
                print("\a", end="")
        else:
            print("\a", end="")
    except Exception:
        pass

def now_timestamp():
    return int(time.time())

# ----------------------------- Word Loading -----------------------------

def load_words_with_categories(filepath=DEFAULT_WORDS_FILE):
    """
    Load words optionally grouped by category from a file.
    File format:
      category:word
      word   (goes into 'default' category)
    Returns: dict category -> list(words)
    """
    cats = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        continue
                    if ":" in s:
                        cat, word = s.split(":", 1)
                        cat = cat.strip().lower()
                        word = word.strip().lower()
                    else:
                        cat = "default"
                        word = s.strip().lower()
                    # keep only alphabetic words or words with apostrophe
                    if all(ch.isalpha() or ch == "'" for ch in word):
                        cats.setdefault(cat, []).append(word)
        except Exception:
            pass
    # Merge builtin categories for fallback and add default if none
    for k, v in BUILTIN_CATEGORIES.items():
        cats.setdefault(k, []).extend([w.lower() for w in v])
    if "default" not in cats:
        cats.setdefault("default", ["python", "hangman", "program"])
    # Remove duplicates and ensure lists are non-empty
    for k in list(cats.keys()):
        cats[k] = sorted(set(cats[k]))
        if not cats[k]:
            del cats[k]
    return cats

# ----------------------------- Leaderboard (persistent) -----------------------------

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_scores(scores):
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except Exception:
        pass

def add_score(name, score, difficulty, category):
    scores = load_scores()
    scores.append({
        "name": name,
        "score": score,
        "difficulty": difficulty,
        "category": category,
        "time": now_timestamp()
    })
    # keep only top 50
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:50]
    save_scores(scores)

# ----------------------------- Save & Resume -----------------------------

def save_game_state(state):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

def load_game_state():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def clear_save():
    try:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
    except Exception:
        pass

# ----------------------------- Core Game Logic -----------------------------

class HangmanGame:
    """
    Simple portable representation of a hangman game state. Works for both Console and GUI.
    """
    def __init__(self, secret_word, lives, difficulty_name="Normal", category="default"):
        self.secret = secret_word.lower()
        self.lives = lives
        self.guessed = set()
        self.wrong = set()
        self.hints_used = 0
        self.started_at = now_timestamp()
        self.difficulty = difficulty_name
        self.category = category
        self.base_score = 0  # computed at end
        self.finished = False
        self.won = False

    def masked_word(self):
        return " ".join([c if c in self.guessed else "_" for c in self.secret])

    def guess_letter(self, ch):
        ch = ch.lower()
        if not ch.isalpha() or len(ch) != 1:
            return False, "invalid"
        if ch in self.guessed or ch in self.wrong:
            return False, "duplicate"
        if ch in self.secret:
            self.guessed.add(ch)
            self._check_win()
            return True, "correct"
        else:
            self.wrong.add(ch)
            self._check_lose()
            return False, "incorrect"

    def use_hint(self):
        """Reveal one unrevealed letter and penalize (counts as wrong guess by default)."""
        unrevealed = [c for c in set(self.secret) if c not in self.guessed]
        if not unrevealed:
            return None
        reveal = random.choice(unrevealed)
        self.guessed.add(reveal)
        self.hints_used += 1
        # optional penalty: count as a wrong guess (reduces lives)
        self.wrong.add(f"hint-{self.hints_used}")  # uses synthetic wrong entries for drawing/lives
        self._check_lose()
        self._check_win()
        return reveal

    def remaining_lives(self):
        # live count is lives - number of 'real' wrong letter guesses (exclude hint markers or count them)
        # We'll treat any wrong set item that is a single letter as a real wrong guess, and hint-* as a penalty too
        return self.lives - len(self.wrong)

    def _check_win(self):
        if all(c in self.guessed for c in self.secret):
            self.finished = True
            self.won = True

    def _check_lose(self):
        if len(self.wrong) >= self.lives:
            self.finished = True
            self.won = False

    def compute_score(self):
        """
        Score formula (example):
          base = len(unique letters) * 10
          bonus = remaining_lives * 5
          penalty = hints_used * 15
          difficulty multiplier applied
        """
        unique_letters = len(set(self.secret))
        base = unique_letters * 10
        bonus = max(0, self.remaining_lives()) * 5
        penalty = self.hints_used * 15
        diff_mult = DIFFICULTY.get(self.difficulty, (6, 1.0))[1]
        raw = (base + bonus - penalty) * diff_mult
        score = max(0, int(raw))
        self.base_score = score
        return score

# ----------------------------- Console Mode -----------------------------

ASCII_PICS = [
    """
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========""",
    # extra stage(s)
    """
     +---+
     |   |
    [O]  |
    /|\\  |
    / \\  |
         |
    =========""",
]

def console_play(categories):
    print("Welcome to Hangman Pro (Console mode)")
    # Optionally resume saved game
    saved = load_game_state()
    if saved:
        use_saved = input("A saved game was found. Resume? (y/n): ").strip().lower()
        if use_saved in ("y", "yes"):
            gstate = saved
            game = HangmanGame(gstate["secret"], gstate["lives"], gstate["difficulty"], gstate.get("category", "default"))
            game.guessed = set(gstate.get("guessed", []))
            game.wrong = set(gstate.get("wrong", []))
            game.hints_used = gstate.get("hints_used", 0)
            print("Resumed saved game.")
            return _console_loop(game, categories)

    # Choose mode: single or two-player
    mode = ""
    while mode not in ("1", "2"):
        mode = input("Choose mode: (1) Single-player (random word)  (2) Two-player: ").strip()
    if mode == "1":
        # pick category
        print("Available categories:", ", ".join(sorted(categories.keys())))
        cat = input("Choose category (or press Enter for random): ").strip().lower()
        if not cat or cat not in categories:
            cat = random.choice(list(categories.keys()))
        secret = random.choice(categories[cat])
    else:
        secret = input("Player 1, enter the secret word (letters only): ").strip().lower()
        while not secret.isalpha():
            print("Please enter alphabetic characters only.")
            secret = input("Player 1, enter the secret word: ").strip().lower()
        cat = "two-player"

    # difficulty
    print("Choose difficulty:")
    for i, k in enumerate(DIFFICULTY.keys(), start=1):
        print(f"{i}. {k} ({DIFFICULTY[k][0]} lives)")
    print(f"{len(DIFFICULTY)+1}. Custom")
    ch = input("Enter choice number: ").strip()
    if ch.isdigit() and 1 <= int(ch) <= len(DIFFICULTY):
        diff_name = list(DIFFICULTY.keys())[int(ch)-1]
        lives = DIFFICULTY[diff_name][0]
    else:
        diff_name = "Custom"
        while True:
            try:
                lives = int(input("Enter number of lives (1-20): ").strip())
                if 1 <= lives <= 20:
                    break
            except Exception:
                pass
            print("Invalid number.")

    game = HangmanGame(secret, lives, difficulty_name=diff_name, category=cat)
    return _console_loop(game, categories)

def _console_loop(game, categories):
    # Core console loop
    while True:
        print("\n" + ("-"*40))
        stage = min(len(game.wrong), len(ASCII_PICS)-1)
        print(ASCII_PICS[stage])
        print("Word:", game.masked_word())
        print(f"Wrong guesses: {' '.join(sorted([w for w in game.wrong if isinstance(w, str) and not w.startswith('hint-')]))}")
        print(f"Lives left: {game.remaining_lives()}   Hints used: {game.hints_used}")
        print("Commands: guess <letter> | hint | save | quit")
        cmd = input("Enter command or letter: ").strip().lower()

        if cmd in ("quit", "q", "exit"):
            print("Goodbye.")
            break
        if cmd == "save":
            # Save state and exit
            state = {
                "secret": game.secret,
                "lives": game.lives,
                "difficulty": game.difficulty,
                "category": game.category,
                "guessed": list(game.guessed),
                "wrong": list(game.wrong),
                "hints_used": game.hints_used,
            }
            save_game_state(state)
            print("Game saved to disk. You can resume later.")
            break
        if cmd == "hint":
            reveal = game.use_hint()
            if reveal:
                print(f"Hint: revealed letter '{reveal}' (penalty applied).")
                play_beep()
            else:
                print("No letters to reveal.")
            if game.finished:
                _console_end(game)
                clear_save()
                break
            continue
        # allow single letter
        if len(cmd) == 1 and cmd.isalpha():
            ok, reason = game.guess_letter(cmd)
            if ok:
                print("Correct!")
                play_beep()
            else:
                if reason == "duplicate":
                    print("You already guessed that.")
                elif reason == "invalid":
                    print("Invalid guess.")
                else:
                    print("Incorrect.")
                    play_beep()
            if game.finished:
                _console_end(game)
                clear_save()
                break
            continue
        print("Unknown command. Try again.")

def _console_end(game):
    if game.won:
        print("\nCONGRATS! You guessed the word:", game.secret)
    else:
        print("\nYou lost. The word was:", game.secret)
    score = game.compute_score()
    print(f"Your score: {score}")
    name = input("Enter your name for leaderboard (or press Enter to skip): ").strip()
    if name:
        add_score(name, score, game.difficulty, game.category)
        print("Score saved.")
    # clear any save
    clear_save()

# ----------------------------- GUI Mode (Tkinter) -----------------------------

if tk:
    class HangmanGUI(tk.Tk):
        def __init__(self, categories):
            super().__init__()
            self.title("Hangman Pro")
            self.categories = categories
            self.geometry("640x480")
            self.resizable(False, False)

            # Top frame: controls
            top = ttk.Frame(self, padding=8)
            top.pack(side="top", fill="x")

            ttk.Label(top, text="Mode:").pack(side="left")
            self.mode_var = tk.StringVar(value="Single")
            ttk.Combobox(top, values=["Single", "Two-player"], textvariable=self.mode_var, width=10, state="readonly").pack(side="left", padx=6)

            ttk.Label(top, text="Category:").pack(side="left")
            cats = sorted(self.categories.keys())
            self.cat_var = tk.StringVar(value=cats[0] if cats else "default")
            self.cat_cb = ttk.Combobox(top, values=cats, textvariable=self.cat_var, width=14, state="readonly")
            self.cat_cb.pack(side="left", padx=6)

            ttk.Label(top, text="Difficulty:").pack(side="left", padx=(10,0))
            self.diff_var = tk.StringVar(value="Normal")
            self.diff_cb = ttk.Combobox(top, values=list(DIFFICULTY.keys())+["Custom"], textvariable=self.diff_var, width=8, state="readonly")
            self.diff_cb.pack(side="left", padx=6)

            ttk.Button(top, text="New Game", command=self.new_game).pack(side="left", padx=6)
            ttk.Button(top, text="Save/Exit", command=self.save_and_exit).pack(side="left", padx=6)
            ttk.Button(top, text="Leaderboard", command=self.show_leaderboard).pack(side="left", padx=6)
            ttk.Button(top, text="Resume", command=self.try_resume).pack(side="left", padx=6)

            # Canvas for drawing hangman
            self.canvas = tk.Canvas(self, width=320, height=320, bg="white")
            self.canvas.pack(side="left", padx=(10,0), pady=10)

            # Right frame for word, input, status
            right = ttk.Frame(self, padding=10)
            right.pack(side="left", fill="both", expand=True)

            self.word_label = ttk.Label(right, text="Word: ", font=("Consolas", 18))
            self.word_label.pack(anchor="w")

            self.wrong_label = ttk.Label(right, text="Wrong: ")
            self.wrong_label.pack(anchor="w", pady=(6,0))

            self.status_label = ttk.Label(right, text="Lives: ")
            self.status_label.pack(anchor="w", pady=(6,0))

            inp_frame = ttk.Frame(right)
            inp_frame.pack(anchor="w", pady=10)
            ttk.Label(inp_frame, text="Letter:").pack(side="left")
            self.guess_entry = ttk.Entry(inp_frame, width=4)
            self.guess_entry.pack(side="left", padx=6)
            self.guess_entry.bind("<Return>", lambda e: self.on_guess())
            ttk.Button(inp_frame, text="Guess", command=self.on_guess).pack(side="left", padx=4)
            ttk.Button(inp_frame, text="Hint", command=self.on_hint).pack(side="left", padx=4)

            # status / messages
            self.message = tk.StringVar(value="")
            ttk.Label(right, textvariable=self.message, foreground="blue").pack(anchor="w", pady=(6,0))

            # keyboard binding for convenience
            for i in range(26):
                self.bind(chr(ord('a')+i), self._key_handler)

            # initialize game variable
            self.game = None

            # try auto-resume if save file exists
            if load_game_state():
                # don't auto-resume—let user decide
                pass

            # start an initial game
            self.new_game()

        def _key_handler(self, event):
            ch = event.char.lower()
            if ch.isalpha() and len(ch)==1:
                self.guess_entry.delete(0, tk.END)
                self.guess_entry.insert(0, ch)
                self.on_guess()

        def try_resume(self):
            saved = load_game_state()
            if not saved:
                messagebox.showinfo("Resume", "No saved game found.")
                return
            # confirm
            if not messagebox.askyesno("Resume", "Resume saved game?"):
                return
            game = HangmanGame(saved["secret"], saved["lives"], saved.get("difficulty","Normal"), saved.get("category","default"))
            game.guessed = set(saved.get("guessed", []))
            game.wrong = set(saved.get("wrong", []))
            game.hints_used = saved.get("hints_used", 0)
            self.game = game
            self.update_ui()
            messagebox.showinfo("Resume", "Resumed saved game.")

        def new_game(self):
            mode = self.mode_var.get()
            cat = self.cat_var.get()
            if mode == "Two-player":
                # ask for secret
                word = simpledialog.askstring("Two-player", "Player 1: Enter secret word (letters only):", show="*")
                if not word:
                    return
                word = word.strip().lower()
                while not word.isalpha():
                    messagebox.showinfo("Invalid", "Word must be alphabetic.")
                    word = simpledialog.askstring("Two-player", "Player 1: Enter secret word (letters only):", show="*")
                    if word is None:
                        return
                    word = word.strip().lower()
                secret = word
            else:
                # pick from category
                if cat not in self.categories or not self.categories[cat]:
                    cat = random.choice(list(self.categories.keys()))
                secret = random.choice(self.categories[cat])

            # difficulty
            diff = self.diff_var.get()
            if diff in DIFFICULTY:
                lives = DIFFICULTY[diff][0]
            else:
                val = simpledialog.askinteger("Custom Lives", "Enter lives (1-20):", minvalue=1, maxvalue=20)
                if val is None:
                    lives = DIFFICULTY["Normal"][0]
                else:
                    lives = val
                diff = "Custom"

            self.game = HangmanGame(secret, lives, difficulty_name=diff, category=cat)
            self.update_ui()
            self.message.set("New game started. Good luck!")

        def on_guess(self):
            if not self.game or self.game.finished:
                self.message.set("Start a new game first.")
                return
            guess = self.guess_entry.get().strip().lower()
            self.guess_entry.delete(0, tk.END)
            if not guess or len(guess) != 1 or not guess.isalpha():
                self.message.set("Enter a single letter (a-z).")
                return
            ok, reason = self.game.guess_letter(guess)
            if ok:
                self.message.set(f"Good! '{guess}' is in the word.")
                play_beep()
            else:
                if reason == "duplicate":
                    self.message.set("You already guessed that letter.")
                elif reason == "invalid":
                    self.message.set("Invalid input.")
                else:
                    self.message.set(f"Sorry — '{guess}' is not in the word.")
                    play_beep()
            self.update_ui()
            if self.game.finished:
                self._end_game_prompt()

        def on_hint(self):
            if not self.game or self.game.finished:
                self.message.set("No active game.")
                return
            reveal = self.game.use_hint()
            if reveal is None:
                self.message.set("No letters left to reveal.")
                return
            self.message.set(f"Hint: letter '{reveal}' revealed (penalty applied).")
            play_beep()
            self.update_ui()
            if self.game.finished:
                self._end_game_prompt()

        def update_ui(self):
            if not self.game:
                return
            self.word_label.config(text="Word: " + self.game.masked_word())
            wrong_letters = " ".join(sorted([w for w in self.game.wrong if isinstance(w, str) and not w.startswith("hint-")]))
            self.wrong_label.config(text="Wrong: " + wrong_letters)
            self.status_label.config(text=f"Lives: {self.game.remaining_lives()}  Hints: {self.game.hints_used}")
            self.draw_hangman()
            if self.game.finished:
                if self.game.won:
                    self.message.set("You won! Well done.")
                else:
                    self.message.set("You lost. Try again.")

        def draw_hangman(self):
            # Clear canvas and draw simple gallows + parts depending on wrong count
            self.canvas.delete("all")
            # base
            self.canvas.create_line(20, 300, 300, 300, width=3)
            self.canvas.create_line(60, 300, 60, 40, width=3)
            self.canvas.create_line(60, 40, 180, 40, width=3)
            self.canvas.create_line(180, 40, 180, 70, width=3)
            stage = min(len(self.game.wrong), MAX_STAGES)
            # head
            if stage >= 1:
                self.canvas.create_oval(150, 70, 210, 130, width=2)
            # body
            if stage >= 2:
                self.canvas.create_line(180, 130, 180, 200, width=2)
            # left arm
            if stage >= 3:
                self.canvas.create_line(180, 150, 150, 180, width=2)
            # right arm
            if stage >= 4:
                self.canvas.create_line(180, 150, 210, 180, width=2)
            # left leg
            if stage >= 5:
                self.canvas.create_line(180, 200, 150, 240, width=2)
            # right leg
            if stage >= 6:
                self.canvas.create_line(180, 200, 210, 240, width=2)
            # eyes
            if stage >= 7:
                self.canvas.create_line(165, 90, 175, 100, width=2)
                self.canvas.create_line(165, 100, 175, 90, width=2)
                self.canvas.create_line(195, 90, 205, 100, width=2)
                self.canvas.create_line(195, 100, 205, 90, width=2)
            if stage >= 8:
                self.canvas.create_arc(160, 105, 200, 125, start=0, extent=180, style=tk.CHORD)

        def _end_game_prompt(self):
            # Called when game finished
            if self.game.won:
                msg = f"You guessed the word: {self.game.secret}\n"
            else:
                msg = f"You lost. The word was: {self.game.secret}\n"
            score = self.game.compute_score()
            msg += f"Score: {score}\nSave score to leaderboard?"
            if messagebox.askyesno("Game Over", msg):
                name = simpledialog.askstring("Leaderboard", "Enter your name (max 20 chars):")
                if name:
                    add_score(name[:20], score, self.game.difficulty, self.game.category)
                    messagebox.showinfo("Saved", "Score saved to leaderboard.")
            # clear saved state after end
            clear_save()

        def save_and_exit(self):
            if not self.game:
                self.destroy()
                return
            state = {
                "secret": self.game.secret,
                "lives": self.game.lives,
                "difficulty": self.game.difficulty,
                "category": self.game.category,
                "guessed": list(self.game.guessed),
                "wrong": list(self.game.wrong),
                "hints_used": self.game.hints_used
            }
            save_game_state(state)
            messagebox.showinfo("Saved", "Game saved. Exiting now.")
            self.destroy()

        def show_leaderboard(self):
            scores = load_scores()
            text = "Top Scores:\n\n"
            for i, s in enumerate(scores[:20], start=1):
                ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(s.get("time", now_timestamp())))
                text += f"{i}. {s['name']} — {s['score']} pts — {s['difficulty']} — {s['category']} — {ts}\n"
            if not scores:
                text = "No scores yet."
            messagebox.showinfo("Leaderboard", text)

# ----------------------------- Main -----------------------------

def main():
    parser = argparse.ArgumentParser(description="Hangman Pro — GUI + Console")
    parser.add_argument("--console", action="store_true", help="Run console mode")
    parser.add_argument("--words", type=str, default=DEFAULT_WORDS_FILE, help="Words file (category:word or word per line)")
    args = parser.parse_args()

    categories = load_words_with_categories(args.words)

    if args.console or tk is None:
        console_play(categories)
    else:
        app = HangmanGUI(categories)
        app.mainloop()

if __name__ == "__main__":
    main()
