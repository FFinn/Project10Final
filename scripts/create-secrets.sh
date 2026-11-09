#!/usr/bin/env bash
set -euo pipefail
umask 077
: "${HARBOR_REGISTRY:?Укажите HARBOR_REGISTRY}"
: "${HARBOR_PULL_USER:?Укажите HARBOR_PULL_USER}"
: "${HARBOR_PULL_PASSWORD:?Укажите HARBOR_PULL_PASSWORD}"
: "${POSTGRES_PASSWORD:?Укажите POSTGRES_PASSWORD}"
: "${TLS_CERT:?Укажите путь TLS_CERT к сертификату}"
: "${TLS_KEY:?Укажите путь TLS_KEY к ключу}"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
printf '%s' "$POSTGRES_PASSWORD" > "$work/password"
python3 - "$work/config.json" <<'PY'
import os,sys,json,base64
value=base64.b64encode((os.environ['HARBOR_PULL_USER']+':'+os.environ['HARBOR_PULL_PASSWORD']).encode()).decode()
with open(sys.argv[1],'w') as f:
    json.dump({'auths':{os.environ['HARBOR_REGISTRY']:{'auth':value}}},f)
PY
kubectl create secret generic petclinic-db --from-file="password=$work/password" --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic harbor-pull --type=kubernetes.io/dockerconfigjson --from-file=".dockerconfigjson=$work/config.json" --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret tls petclinic-tls --cert="$TLS_CERT" --key="$TLS_KEY" --dry-run=client -o yaml | kubectl apply -f -
