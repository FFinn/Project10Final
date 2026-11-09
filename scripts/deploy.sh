#!/usr/bin/env bash
set -euo pipefail
: "${APP_IMAGE:?Укажите образ из Harbor с SHA-256}"
[[ "$APP_IMAGE" =~ @sha256:[a-f0-9]{64}$ ]] || { echo 'Требуется образ по SHA-256'; exit 1; }
kubectl get secret petclinic-db harbor-pull petclinic-tls >/dev/null
kubectl apply -f k8s/kyverno-policy.yaml
kubectl apply -f k8s/network-policies.yaml -f k8s/postgres-service.yaml -f k8s/postgres-statefulset.yaml
kubectl rollout status statefulset/postgres --timeout=180s
manifest=$(mktemp)
trap 'rm -f "$manifest"' EXIT
sed -E "s|image: .*petclinic@sha256:[a-f0-9]+|image: $APP_IMAGE|" k8s/deployment.yaml > "$manifest"
kubectl apply -f "$manifest" -f k8s/service.yaml -f k8s/ingress.yaml
kubectl rollout status deployment/petclinic --timeout=300s
