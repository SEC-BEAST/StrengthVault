# StrengthVault - Password Strength Checker

*StrengthVault* is a simple yet powerful password strength checker that helps you evaluate the security of your passwords and suggests improvements to make them stronger. It uses advanced algorithms to analyze password strength based on length, complexity, and common vulnerabilities. Additionally, PassGuard offers the ability to generate random strong passwords to ensure better security for your online accounts.

## Features

- *Password Strength Analysis:* Analyzes password strength using industry-standard metrics (e.g., zxcvbn).
- *Password Suggestions:* Provides actionable recommendations to improve password strength (e.g., adding uppercase letters, numbers, special characters).
- *Weak/Banned Password Detection:* Flags commonly used or leaked passwords that should be avoided.
- *Random Password Generator:* Generates random, secure passwords with customizable length.
- *Results Export:* Export password strength results to a JSON file for later review or auditing.
- *User-Friendly Interface:* Clean and intuitive GUI built with Tkinter, designed for ease of use.

## Requirements

To run *PassGuard*, you'll need to have the following dependencies installed:

- Python 3.x
- Tkinter (for the GUI)
- zxcvbn (for password strength evaluation)

You can install the required Python packages using pip:

```bash
pip install zxcvbn
