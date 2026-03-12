#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME="${IMAGE_NAME:-zt-demo-fastapi}"
IMAGE_TAG="${IMAGE_TAG:-1.0}"
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" ./app
echo "Built ${IMAGE_NAME}:${IMAGE_TAG}"
