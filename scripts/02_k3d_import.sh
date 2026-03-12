#!/usr/bin/env bash
set -euo pipefail
CLUSTER="${CLUSTER:-zt-demo}"
IMAGE_NAME="${IMAGE_NAME:-zt-demo-fastapi}"
IMAGE_TAG="${IMAGE_TAG:-1.0}"
k3d image import "${IMAGE_NAME}:${IMAGE_TAG}" -c "${CLUSTER}"
echo "Imported ${IMAGE_NAME}:${IMAGE_TAG} into k3d cluster ${CLUSTER}"
