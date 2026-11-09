#!/usr/bin/env python3
"""Проверка запрета записи и события Falco в контейнере PetClinic."""
import json
import subprocess
import time
from datetime import datetime, timezone

started = datetime.now(timezone.utc)
checks = []
for path in ["/tmp/project10-allowed", "/app/project10-denied"]:
    result = subprocess.run(
        ["kubectl", "exec", "deployment/petclinic", "--", "sh", "-c", "printf check > " + path],
        capture_output=True, text=True,
    )
    checks.append({"path": path, "exit_code": result.returncode, "stderr": result.stderr.strip()})

time.sleep(3)
logs = subprocess.run(
    ["kubectl", "logs", "-n", "falco", "-l", "app.kubernetes.io/name=falco",
     "-c", "falco", "--since=2m", "--tail=-1"],
    capture_output=True, text=True, check=True,
)
events = []
for line in logs.stdout.splitlines():
    try:
        event = json.loads(line)
    except ValueError:
        continue
    event_time = event.get("output_fields", {}).get("evt.time", 0) / 1e9
    if event.get("rule") == "PetClinic write outside tmp" and event_time >= started.timestamp():
        events.append(event)

passed = (
    checks[0]["exit_code"] == 0
    and checks[1]["exit_code"] != 0
    and any(e.get("output_fields", {}).get("fs.path.name") == "/app/project10-denied" for e in events)
)
print(json.dumps({"started_at": started.isoformat(), "write_checks": checks,
                  "events": events, "passed": passed}, ensure_ascii=False, indent=2))
raise SystemExit(0 if passed else 1)
