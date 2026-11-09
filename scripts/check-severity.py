#!/usr/bin/env python3
"""Останавливает публикацию при уязвимостях HIGH или CRITICAL."""
import json
import sys
from pathlib import Path
report = json.loads(Path(sys.argv[1]).read_text())
results = report.get("Results", [])
packages = sum(len(result.get("Packages", [])) for result in results)
if not results or packages == 0:
    print("Ошибка: отчёт не содержит проверенных пакетов")
    sys.exit(2)
print(f"Проверено пакетов: {packages}")
findings = [v for result in report.get("Results", []) for v in result.get("Vulnerabilities", []) if v.get("Severity") in {"HIGH", "CRITICAL"}]
for finding in findings:
    print(f"{finding['Severity']}: {finding['VulnerabilityID']} — {finding['PkgName']} {finding['InstalledVersion']}")
print(f"HIGH/CRITICAL: {len(findings)}")
sys.exit(bool(findings))
