import os
import subprocess

# Hardcoded secret
password = "super_secret_123"
api_key = "AKIAIOSFODNN7EXAMPLE"

# Dangerous operations
os.system("rm -rf /tmp/cleanup")
subprocess.call(["sh", "-c", "echo 'dangerous'"])

# Code injection risk
user_input = input()
eval(user_input)
