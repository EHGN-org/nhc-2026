#!/usr/bin/env python3
"""Open the challenge in Chromium, submit NHC391, print the flag from #result."""
from playwright.sync_api import sync_playwright

HOST = "http://localhost:1337"

PASSWORD = "NHC391"

with sync_playwright() as p:
    browser = p.chromium.launch(
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    try:
        page = browser.new_page()
        page.goto(HOST + "/", wait_until="domcontentloaded", timeout=30_000)
        inp = page.locator('input[name="input"]')
        inp.wait_for(state="attached", timeout=30_000)
        inp.fill(PASSWORD, force=True)
        page.locator("button", has_text="Check").click(force=True)
        result = page.locator("p#result")
        result.wait_for(state="attached", timeout=15_000)
        page.wait_for_function(
            """() => {
                const el = document.querySelector("p#result");
                const text = el && el.textContent ? el.textContent.trim() : "";
                return text.length > 0;
            }""",
            timeout=30_000,
        )
        flag = result.inner_text().strip()
    finally:
        browser.close()

assert flag.startswith("NHC{"), f"no flag in result: {flag!r}"
print(flag)
