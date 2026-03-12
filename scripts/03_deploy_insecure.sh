#!/usr/bin/env bash
set -euo pipefail
kubectl apply -k k8s/insecure
kubectl -n insecure rollout status deploy/users
kubectl -n insecure rollout status deploy/pay
kubectl -n insecure rollout status deploy/gateway
kubectl -n insecure get pods -o wide
