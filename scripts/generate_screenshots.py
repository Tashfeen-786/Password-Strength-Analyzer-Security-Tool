"""
REAL UI screenshot capture (Playwright + the actually running application).

Captures the working app at http://localhost:8000 using synthetic demo
passwords only. Produces the browser-capture portion of the 28-item PDF
evidence checklist into screenshots/.

Requires:
    pip install playwright
    python -m playwright install chromium
    (backend running:  uvicorn backend.app:app --port 8000)

    python scripts/generate_screenshots.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
BASE = "http://localhost:8000"
VIEWPORT = {"width": 1440, "height": 900}

# synthetic demo passwords ONLY
DEMO = {
    "very_weak": "123456",
    "weak": "qwerty2026!",
    "moderate": "P@ssw0rd99",
    "strong": "Tr0p!cal-Driftwood-7829",
    "very_strong": "Zx7!kQ29#vLm4&Rp8wT5",
    "sequence": "SkyBlue-12345",
    "repetition": "aaaaaaaaaaaaaaaa",
    "common": "iloveyou",
    "hidden": "synthetic-DEMO-view-92731!",
    "personal": "John@2026",
    "policy": "Password123!",
}


def settle(page, ms: int = 1100) -> None:
    time.sleep(ms / 1000)


def type_and_wait(page, text: str) -> None:
    page.fill("#pw-input", "")
    page.fill("#pw-input", text)
    settle(page)


def main() -> None:
    SHOTS.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto(BASE, wait_until="networkidle")

        # --- dashboard first (pristine seeded demo data) ---
        page.click("#tab-dashboard")
        settle(page, 1600)
        page.screenshot(path=str(SHOTS / "19_analytics_dashboard.png"))
        page.locator("#chart-strength-distribution").screenshot(
            path=str(SHOTS / "20_strength_distribution.png"))
        page.locator("#chart-weakness-types").screenshot(
            path=str(SHOTS / "21_weakness_chart.png"))

        # --- analyzer homepage & hidden password field ---
        page.click("#tab-analyzer")
        settle(page)
        page.screenshot(path=str(SHOTS / "03_analyzer_homepage.png"))
        type_and_wait(page, DEMO["hidden"])
        page.screenshot(path=str(SHOTS / "04_hidden_password.png"))

        # --- the five real classification states ---
        for num, key in [("05", "very_weak"), ("06", "weak"),
                         ("07", "moderate"), ("08", "strong"),
                         ("09", "very_strong")]:
            type_and_wait(page, DEMO[key])
            page.screenshot(path=str(SHOTS / f"{num}_{key}_result.png"))

        # --- 10 length analysis (result card of a 20-char sample) ---
        page.locator("#result-card").screenshot(
            path=str(SHOTS / "10_length_analysis.png"))

        # --- finding-focused captures ---
        def findings_shot(password: str, filename: str,
                          card: str = "#findings-card"):
            type_and_wait(page, password)
            el = page.locator(card)
            el.scroll_into_view_if_needed()
            settle(page, 400)
            el.screenshot(path=str(SHOTS / filename))

        findings_shot(DEMO["sequence"], "11_sequence_detection.png")
        findings_shot(DEMO["weak"], "12_keyboard_pattern_detection.png")
        findings_shot(DEMO["repetition"], "13_repetition_detection.png")
        findings_shot(DEMO["common"], "14_common_password_warning.png")

        # --- 15 security recommendations (with demo personal context) ---
        page.click("text=Optional demo context")
        page.fill("input[placeholder='e.g. Rahul']", "John")
        page.fill("input[placeholder='e.g. 1999']", "2026")
        type_and_wait(page, DEMO["personal"])
        page.locator("#suggestions-card").screenshot(
            path=str(SHOTS / "15_security_recommendations.png"))

        # --- 18 policy checker (POLICY PASS vs WEAK score — teaching shot) ---
        type_and_wait(page, DEMO["policy"])
        page.locator("#policy-card").screenshot(
            path=str(SHOTS / "18_policy_checker.png"))

        # --- 16 entropy explanation (Learn tab) ---
        page.click("#tab-learn")
        settle(page, 700)
        el = page.locator("#entropy-explainer")
        el.scroll_into_view_if_needed()
        settle(page, 400)
        el.screenshot(path=str(SHOTS / "16_entropy_explanation.png"))

        # --- 17 password generator ---
        page.click("#tab-generator")
        settle(page, 500)
        page.click("#generate-btn")
        settle(page, 900)
        page.screenshot(path=str(SHOTS / "17_password_generator.png"))

        browser.close()
    print("Browser-capture evidence written to", SHOTS)


if __name__ == "__main__":
    sys.exit(main())
