"""
Seed the analytics database with SYNTHETIC demo analyses.

Runs the real analyzer over a fixed set of synthetic demo passwords and
persists only the safe aggregate metadata (exactly what POST /api/analyze
persists). Used so the dashboard has meaningful, honest demo data for
screenshots and presentations.

    python scripts/seed_demo_data.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.analytics_service import record_analysis
from backend.services.password_analyzer import analyze_password

# Synthetic demo passwords ONLY. Never real credentials.
DEMO_PASSWORDS = [
    "123456", "password", "qwerty", "iloveyou", "letmein",
    "Password123!", "qwerty2026!", "welcome123", "admin2026", "hello1234",
    "aaaaaaaaaaaaaaaa", "abcabcabc", "987654321", "dragon", "football",
    "P@ssw0rd99", "Summer2025!", "MonkeyBusiness77", "Sunshine!99",
    "Tr0p!cal-Driftwood-7829", "Ex0t!c-Nebula-48210", "OceanWave-9Quartz-47",
    "velvet-galaxy-harbor-orchid", "river-crystal-thunder-solar",
    "lunar-cobalt-phoenix-silver", "Zx7!kQ29#vLm4&Rp8", "aB3$eF7!hJ9#kL2@",
    "Nimbus-47-Fern-Quasar-9", "Rosetta-Comet-48216", "WinterMango77",
]


def main() -> None:
    for pw in DEMO_PASSWORDS:
        record_analysis(analyze_password(pw))
    print(f"Seeded {len(DEMO_PASSWORDS)} synthetic demo analyses "
          "(safe metadata only).")


if __name__ == "__main__":
    main()
