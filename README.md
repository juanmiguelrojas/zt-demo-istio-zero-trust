# Zero Trust Demo (k3d + Istio)

## Run (high level)
1) Build + import image to k3d
2) Deploy insecure + show it is open
3) Deploy secure + apply mTLS STRICT + deny-by-default + allowlist

## Files
- app/: FastAPI app
- k8s/: manifests for insecure/secure
- istio/: security policies
- scripts/: helper scripts
