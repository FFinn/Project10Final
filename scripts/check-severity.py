#!/usr/bin/env python3
"""Останавливает публикацию при уязвимостях HIGH или CRITICAL."""
import json
import sys
from pathlib import Path
report = json.loads(Path(sys.argv[1]).read_text())
findings = [v for result in report.get("Results", []) for v in result.get("Vulnerabilities", []) if v.get("Severity") in {"HIGH", "CRITICAL"}]
for finding in findings:
    print(f"{finding['Severity']}: {finding['VulnerabilityID']} — {finding['PkgName']} {finding['InstalledVersion']}")
print(f"HIGH/CRITICAL: {len(findings)}")
sys.exit(bool(findings))
