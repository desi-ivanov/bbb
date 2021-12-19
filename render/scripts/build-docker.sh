#!/bin/bash
set -eou pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

docker build -t render-bbb -f docker/render-bbb/Dockerfile  .

docker build -t render-bbb-lambda -f ./docker/render-bbb-lambda/Dockerfile .