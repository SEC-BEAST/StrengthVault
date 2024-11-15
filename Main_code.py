import tkinter as tk
from tkinter import filedialog, messagebox
import re
import random
import string
import logging
import json
from functools import lru_cache

from zxcvbn import zxcvbn

logging.basicConfig(filename='password_checker.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Wordlist:
    """Class to handle wordlists for password checking."""

    _cache = {}

    def _init_(self, file_path):
        self.file_path = file_path
        self.words = self.load_wordlist()

    def load_wordlist(self):
        """Load wordlist from file."""
        if self.file_path in self._cache:
            return self._cache[self.file_path]

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                wordlist = [line.strip() for line in file]
                self._cache[self.file_path] = wordlist
                return wordlist
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: File '{self.file_path}' not found.") from e
        except Exception as e:
            raise RuntimeError(
                f"Error loading wordlist from '{self.file_path}': {str(e)}"
            ) from e

    def is_word_in_list(self, word):
        """Check if a word is in the wordlist."""
        return word in self.words

class StrengthResult:
    """Class to store password strength check results."""

    def _init_(self, strength: str, score: int, message: str):
        self.strength = strength
        self.score = score
        self.message = message

class PasswordStrength:
    """Class to handle password strength checking and related operations."""

    def _init_(self, weak_wordlist_path: str = "./weak_passwords.txt",
                 banned_wordlist_path: str = "./banned_passwords.txt"):
        self.weak_wordlist = (Wordlist(weak_wordlist_path)
                              if weak_wordlist_path else None)
        self.banned_wordlist = (Wordlist(banned_wordlist_path)
                                if banned_wordlist_path else None)
        self.min_password_length = 12
        self.strength_mapping = {
            0: "Very Weak",
            1: "Weak",
            2: "Moderate",
            3: "Strong",
            4: "Very Strong"
        }

    @lru_cache(maxsize=1000)
    def check_password_strength(self, password: str) -> StrengthResult:
        """Check the strength of a given password."""
        if len(password) < self.min_password_length:
            return StrengthResult("Too short", 0, "Password should be at least 12 characters long.")

        if self.weak_wordlist and self.weak_wordlist.is_word_in_list(password):
            return StrengthResult("Weak", 0, "Password is commonly used and easily guessable.")

        if self.banned_wordlist and self.banned_wordlist.is_word_in_list(password):
            return StrengthResult("Banned", 0,
                                  "This password is not allowed, as it is commonly found in data leaks.")

        password_strength = zxcvbn(password)
        score = password_strength["score"]
        strength = self.strength_mapping[score]
        complexity_issues = []
        if not re.search(r'[A-Z]', password):
            complexity_issues.append("uppercase letter")
        if not re.search(r'[a-z]', password):
            complexity_issues.append("lowercase letter")
        if not re.search(r'\d', password):
            complexity_issues.append("number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            complexity_issues.append("special character")

        if complexity_issues:
            return StrengthResult("Weak", score,
                                  f"Password lacks complexity. Missing: {', '.join(complexity_issues)}.")

        if score >= 3:
            return StrengthResult(strength, score,
                                  f"Password meets all the requirements. Score: {score}/4")

        suggestions = password_strength["feedback"]["suggestions"]
        return StrengthResult(strength, score,
                              f"Password is {strength.lower()}. Suggestions: {', '.join(suggestions)}")

    def generate_random_password(self, length=16):
        """Generate a random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def suggest_improvements(self, password: str) -> str:
        """Suggest improvements for a given password."""
        result = self.check_password_strength(password)
        suggestions = []

        if len(password) < self.min_password_length:
            suggestions.append(f"Increase length to at least {self.min_password_length} characters")

        if not re.search(r'[A-Z]', password):
            suggestions.append("Add uppercase letters")
        if not re.search(r'[a-z]', password):
            suggestions.append("Add lowercase letters")
        if not re.search(r'\d', password):
            suggestions.append("Add numbers")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            suggestions.append("Add special characters")

        if not suggestions:
            suggestions = result.message.split("Suggestions: ")[-1].split(", ")

        return "Suggested improvements:\n\n" + "\n".join(f"- {s}" for s in suggestions)

class PasswordStrengthGUI:
    """GUI class for Password Strength Checker."""

    def _init_(self, master):
        self.master = master
        master.title("Password Strength Checker")

        self.password_strength = PasswordStrength()

        # Main UI Components
        self.label = tk.Label(master, text="Enter password:")
        self.label.pack()

        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack()
        self.password_entry.bind('<Return>', lambda event: self.check_password())

        self.check_button = tk.Button(master, text="Check Strength", command=self.check_password)
        self.check_button.pack()

        self.result_label = tk.Label(master, text="")
        self.result_label.pack()

        self.suggestion_label = tk.Label(master, text="")
        self.suggestion_label.pack()

        self.generate_button = tk.Button(master, text="Generate Strong Password", command=self.generate_password)
        self.generate_button.pack()

        self.export_button = tk.Button(master, text="Export Results", command=self.export_results)
        self.export_button.pack()

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

        self.tip_label = tk.Label(master, text="\nTips:\n"
                                              "\n• Do not include any personal information in your password"
                                              "\n• Use a combination of uppercase and lowercase letters"
                                              "\n• Include numbers and special characters"
                                              "\n• Avoid common words or phrases"
                                              "\n• Use a unique password for each account",
                                   fg="light blue", justify="left")
        self.tip_label.pack()

        # Adding the 'Made by' label at the bottom
        self.made_by_label = tk.Label(master, text="Made by Ayush Singh", fg="gray", font=("Arial", 8))
        self.made_by_label.pack(side="bottom", pady=10)

        self.results = []

    def check_password(self):
        """Check the strength of the entered password."""
        password = self.password_entry.get()
        result = self.password_strength.check_password_strength(password)
        self.result_label.config(text=f"{result.strength}: {result.message}")
        suggestions = self.password_strength.suggest_improvements(password)
        self.suggestion_label.config(text=suggestions)
        self.results.append({"password": password, "strength": result.strength,
                             "message": result.message})
        logging.info("Password checked: %s", result.strength)

    def generate_password(self):
        """Generate a random strong password."""
        password = self.password_strength.generate_random_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        copy_to_clipboard = messagebox.askyesno("Generated Password",
                                                f"Generated password: {password}\n\n"
                                                "Do you want to copy the password to clipboard?")
        if copy_to_clipboard:
            self.master.clipboard_clear()
            self.master.clipboard_append(password)
            messagebox.showinfo("Clipboard", "Password copied to clipboard.")

    def export_results(self):
        """Export the password check results to a JSON file."""
        if not self.results:
            messagebox.showwarning("No Results", "No passwords have been checked yet.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)
            messagebox.showinfo("Export Successful", f"Results exported to {file_path}")


if _name_ == '_main_':
    root = tk.Tk()
    gui = PasswordStrengthGUI(root)
    root.mainloop()
