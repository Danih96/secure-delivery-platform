"""
Intentionally vulnerable sample app for Week 1 scanner testing.
DO NOT deploy this — it exists only to give scanners something to find.
"""

import subprocess
import os

# SAST finding: hardcoded secret (Semgrep will flag this)
SECRET_KEY = "supersecret123"
DB_PASSWORD = "admin1234"

# SAST finding: command injection via user input
def run_command(user_input):
    result = subprocess.run(user_input, shell=True, capture_output=True)
    return result.stdout

# SAST finding: path traversal
def read_file(filename):
    with open("/etc/" + filename) as f:
        return f.read()

if __name__ == "__main__":
    print("Vulnerable app running — for scanner testing only")
