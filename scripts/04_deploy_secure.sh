#!/usr/bin/env bash
set -euo pipefail
kubectl apply -k k8s/secure
kubectl -n secure rollout status deploy/users
kubectl -n secure rollout status deploy/pay
kubectl -n secure rollout status deploy/gateway
kubectl -n secure get pods -o wide
