#!/usr/bin/env python3
"""Проверка разрешённых и запрещённых соединений в учебном кластере."""
import json
import subprocess
import time


def kubectl(*args, input=None):
    return subprocess.check_output(["kubectl", *args], input=input, text=True)


app_ip = json.loads(kubectl("get", "service", "petclinic", "-o", "json"))["spec"]["clusterIP"]
pg_ip = json.loads(kubectl("get", "service", "postgres", "-o", "json"))["spec"]["clusterIP"]
probe = '''import socket,json,urllib.request
checks=[]
for label,host,port,allowed in TARGETS:
 try:
  with socket.create_connection((host,port),timeout=4): pass
  connected=True
 except OSError:
  connected=False
 checks.append({"check":label,"host":host,"port":port,"expected_access":allowed,"connected":connected,"passed":connected==allowed})
print(json.dumps(checks),flush=True)
raise SystemExit(0 if all(x["passed"] for x in checks) else 1)
'''
all_results = []
for name, labels, targets in [
    ("verify-authorized-scanner", {"security-scan": "true"}, [
        ("scanner_to_app", "petclinic", 8080, True),
        ("scanner_to_postgres_denied", pg_ip, 5432, False),
        ("scanner_external_egress_denied", "1.1.1.1", 443, False)]),
    ("verify-isolated-pod", {}, [("unlabeled_pod_to_app_denied", app_ip, 8080, False)])
]:
    name += "-" + str(int(time.time()))
    pod = {"apiVersion":"v1","kind":"Pod","metadata":{"name":name,"namespace":"default","labels":labels},
           "spec":{"restartPolicy":"Never","automountServiceAccountToken":False,
                   "securityContext":{"runAsNonRoot":True,"runAsUser":1000,"seccompProfile":{"type":"RuntimeDefault"}},
                   "containers":[{"name":"probe","image":"python:3.12-alpine",
                     "securityContext":{"runAsNonRoot":True,"readOnlyRootFilesystem":True,"allowPrivilegeEscalation":False,"capabilities":{"drop":["ALL"]}},
                     "resources":{"requests":{"cpu":"25m","memory":"32Mi"},"limits":{"cpu":"100m","memory":"64Mi"}},
                     "command":["python","-c",probe.replace("TARGETS",repr(targets))]}]}}
    kubectl("apply", "-f", "-", input=json.dumps(pod))
    for _ in range(120):
        status = json.loads(kubectl("get", "pod", name, "-o", "json"))["status"]["phase"]
        if status in {"Succeeded", "Failed"}:
            break
        time.sleep(2)
    else:
        raise RuntimeError(f"Проверка соединения не завершилась: {name}")
    all_results.extend(json.loads(kubectl("logs", name)))
print(json.dumps(all_results, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(x["passed"] for x in all_results) else 1)
