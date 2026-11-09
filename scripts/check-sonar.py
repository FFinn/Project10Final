#!/usr/bin/env python3
"""Сохраняет результаты SonarQube и проверяет запреты на выпуск."""
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

base = os.environ["SONAR_HOST_URL"].rstrip("/")
project = os.environ["SONAR_PROJECT_KEY"]
token = os.environ["SONAR_TOKEN"]
reports = Path("reports")
reports.mkdir(exist_ok=True)


def read_api(path, params=None):
    url = base + "/api/" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def save(name, data):
    (reports / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


metric_names = ["bugs", "vulnerabilities", "code_smells", "security_hotspots", "tests",
                "test_failures", "test_errors", "coverage", "new_coverage",
                "duplicated_lines_density", "blocker_violations", "critical_violations"]
measures = read_api("measures/component", {"component": project, "metricKeys": ",".join(metric_names)})
quality = read_api("qualitygates/project_status", {"projectKey": project})
issues = read_api("issues/search", {"componentKeys": project, "resolved": "false", "ps": 500})
save("sonarqube-measures.json", measures)
save("sonarqube-quality.json", quality)
save("sonarqube-issues.json", issues)
values = {item["metric"]: item.get("value") for item in measures["component"]["measures"]}
required = ["vulnerabilities", "blocker_violations", "critical_violations"]
if any(values.get(name) is None for name in required):
    raise SystemExit("Ошибка: SonarQube не вернул обязательные метрики")
blocked = [name for name in required if float(values[name]) > 0]
passed = quality["projectStatus"]["status"] == "OK" and not blocked
save("sonarqube-release-check.json", {"server": base, "project": project,
     "metrics": {name: values[name] for name in required},
     "quality_gate": quality["projectStatus"]["status"], "passed": passed})
print("SonarQube: " + ("выпуск разрешён" if passed else "выпуск запрещён"))
raise SystemExit(0 if passed else 1)
