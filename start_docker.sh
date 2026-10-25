#!/bin/bash

FORCE_REBUILD=false
IMAGE_NAME="myplanutils"

if [[ "$1" == "--rebuild" ]]; then
    FORCE_REBUILD=true
fi

if [[ "$FORCE_REBUILD" == "true" ]] || \
   ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then

    echo "Building image $IMAGE_NAME..."
    BUILD_ARGS=(
        --rm
        --platform linux/amd64
        --tag "$IMAGE_NAME"
        .
        --file Dockerfile
    )

    if [[ "$FORCE_REBUILD" == "true" ]]; then
        BUILD_ARGS+=(--no-cache)
        BUILD_ARGS+=(--network=host)
    fi

    docker build "${BUILD_ARGS[@]}"
fi

docker run -v "$(pwd)":/project -w /project -it --privileged --platform linux/amd64 --rm myplanutils bash
