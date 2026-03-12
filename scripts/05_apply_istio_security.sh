#!/usr/bin/env bash
set -euo pipefail
kubectl apply -f istio/peerauth-strict.yaml
kubectl apply -f istio/authz-deny-by-default.yaml
kubectl apply -f istio/authz-allow-gateway-public.yaml
kubectl apply -f istio/authz-allow-gateway-to-users-pay.yaml
kubectl -n secure get peerauthentication,authorizationpolicy
